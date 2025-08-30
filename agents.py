from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
from schemas import Role, Team, PlayerState, Message, Phase, ModerationResult, ModerationAction, Leaderboard, LeaderboardEntry
from prompts import (
    player_day_message_prompt,
    player_vote_prompt,
    fortune_teller_night_prompt,
    werewolf_night_prompt,
    overseer_moderate_prompt,
    overseer_leaderboard_prompt
)


class Player(ABC):
    def __init__(self, state: PlayerState, llm_provider):
        self.state = state
        self.llm = llm_provider
        self.message_history: List[Message] = []
    
    def get_state_summary(self, game_state: Dict[str, Any]) -> str:
        summary = f"You are {self.state.name}.\n"
        summary += f"Alive players: {', '.join([p.name for p in game_state['players'] if p.alive])}\n"
        summary += f"Dead players: {', '.join([p.name for p in game_state['players'] if not p.alive])}\n"
        
        if self.message_history:
            recent = self.message_history[-5:]
            summary += "\nRecent messages:\n"
            for msg in recent:
                if msg.moderation.action != ModerationAction.VETO:
                    summary += f"- {msg.speaker}: {msg.public_text}\n"
        
        if self.state.private_knowledge:
            summary += f"\nYour private knowledge: {self.state.private_knowledge}\n"
        
        return summary
    
    def create_day_message(self, game_state: Dict[str, Any]) -> Dict[str, str]:
        state_summary = self.get_state_summary(game_state)
        messages = player_day_message_prompt(
            self.state.role.value,
            self.state.team.value,
            state_summary
        )
        return self.llm.json(messages)
    
    def vote(self, candidates: List[str], game_state: Dict[str, Any]) -> str:
        state_summary = self.get_state_summary(game_state)
        messages = player_vote_prompt(
            self.state.role.value,
            candidates,
            state_summary
        )
        response = self.llm.json(messages)
        target = response.get("final", candidates[0])
        
        # Validate target is in candidates
        if target not in candidates:
            print(f"[Warning] {self.state.name} voted for invalid target '{target}', defaulting to {candidates[0]}")
            target = candidates[0]
        
        return target
    
    @abstractmethod
    def night_action(self, game_state: Dict[str, Any]) -> Optional[str]:
        pass


class Villager(Player):
    def night_action(self, game_state: Dict[str, Any]) -> Optional[str]:
        return None  # Villagers have no night action


class Werewolf(Player):
    def night_action(self, game_state: Dict[str, Any]) -> Optional[str]:
        alive_non_wolves = [
            p.name for p in game_state['players']
            if p.alive and p.role != Role.WEREWOLF
        ]
        
        if not alive_non_wolves:
            return None
        
        state_summary = self.get_state_summary(game_state)
        messages = werewolf_night_prompt(alive_non_wolves, state_summary)
        response = self.llm.json(messages)
        target = response.get("final", alive_non_wolves[0])
        
        if target not in alive_non_wolves:
            target = alive_non_wolves[0]
        
        return target


class FortuneTeller(Player):
    def night_action(self, game_state: Dict[str, Any]) -> Optional[str]:
        alive_others = [
            p.name for p in game_state['players']
            if p.alive and p.name != self.state.name
        ]
        
        if not alive_others:
            return None
        
        state_summary = self.get_state_summary(game_state)
        messages = fortune_teller_night_prompt(alive_others, state_summary)
        response = self.llm.json(messages)
        target = response.get("final", alive_others[0])
        
        if target not in alive_others:
            target = alive_others[0]
        
        # Store the inspection result
        target_player = next(p for p in game_state['players'] if p.name == target)
        if "inspections" not in self.state.private_knowledge:
            self.state.private_knowledge["inspections"] = {}
        self.state.private_knowledge["inspections"][target] = target_player.role.value
        
        return target


class Overseer:
    def __init__(self, llm_provider):
        self.llm = llm_provider
        self.all_private_thoughts: List[Dict[str, str]] = []
        self.all_public_messages: List[Message] = []
        self.all_votes: List[Dict[str, str]] = []
        self.all_events: List[Dict[str, Any]] = []
    
    def moderate_message(self, speaker: str, phase: Phase, rationale: str, final_text: str) -> ModerationResult:
        messages = overseer_moderate_prompt(
            speaker,
            phase.value,
            final_text,
            rationale
        )
        
        response = self.llm.json(messages)
        
        # Store private thoughts
        self.all_private_thoughts.append({
            "speaker": speaker,
            "phase": phase.value,
            "rationale": rationale
        })
        
        action = ModerationAction(response.get("decision", "allow"))
        reason = response.get("reason", "No reason provided")
        redacted = response.get("redacted", None)
        
        return ModerationResult(
            action=action,
            reason=reason,
            redacted_text=redacted
        )
    
    def update_leaderboard(self, game_state: Dict[str, Any]) -> Leaderboard:
        context = {
            "private_thoughts": self.all_private_thoughts[-20:],  # Last 20 for context limit
            "public_messages": [
                {
                    "speaker": m.speaker,
                    "text": m.public_text,
                    "moderation": m.moderation.action.value
                }
                for m in self.all_public_messages[-10:]
            ],
            "recent_votes": self.all_votes[-10:],
            "recent_events": self.all_events[-5:],
            "alive_players": [p.name for p in game_state['players'] if p.alive]
        }
        
        messages = overseer_leaderboard_prompt(context)
        response = self.llm.json(messages)
        
        scores = []
        for score_data in response.get("scores", []):
            scores.append(LeaderboardEntry(
                player=score_data["player"],
                suspicion=min(1.0, max(0.0, score_data["suspicion"]))
            ))
        
        return Leaderboard(
            scores=scores,
            top_guess=response.get("top_guess", None)
        )
    
    def record_vote(self, voter: str, target: str):
        self.all_votes.append({"voter": voter, "target": target})
    
    def record_event(self, event_type: str, details: Dict[str, Any]):
        self.all_events.append({"type": event_type, **details})