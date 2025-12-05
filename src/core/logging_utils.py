import json
from typing import Any, List, Dict
from schemas import GameLog, GameEvent, PlayerState
from config import GameConfig


class GameLogger:
    def __init__(self, config: GameConfig):
        self.config = config
        self.timeline: List[GameEvent] = []
        self.leaderboard_snapshots: List[Dict[str, Any]] = []
    
    def log_message(self, message: Any):
        self.timeline.append(GameEvent(
            type="message",
            payload={
                "speaker": message.speaker,
                "phase": message.phase.value,
                "public_text": message.public_text,
                "private_thoughts": message.private_thoughts,
                "moderation": {
                    "action": message.moderation.action.value,
                    "reason": message.moderation.reason,
                    "redacted_text": message.moderation.redacted_text
                }
            }
        ))
    
    def log_vote(self, vote: Any):
        self.timeline.append(GameEvent(
            type="vote",
            payload={
                "voter": vote.voter,
                "target": vote.target
            }
        ))
    
    def log_event(self, event_type: str, details: Dict[str, Any]):
        self.timeline.append(GameEvent(
            type="event",
            payload={
                "event_type": event_type,
                **details
            }
        ))
    
    def log_leaderboard(self, day: int, after: str, leaderboard: Any):
        self.leaderboard_snapshots.append({
            "day": day,
            "after": after,
            "leaderboard": {
                "scores": [{"player": e.player, "suspicion": e.suspicion} for e in leaderboard.scores],
                "top_guess": leaderboard.top_guess
            }
        })
    
    def write_final_log(self, players: List[PlayerState], winner: str):
        game_log = GameLog(
            config=self.config.__dict__,
            players=[{
                "name": p.name,
                "role": p.role.value,
                "alive": p.alive,
                "notes": p.notes,
                "private_knowledge": p.private_knowledge
            } for p in players],
            timeline=[{
                "type": e.type,
                "payload": e.payload
            } for e in self.timeline],
            leaderboard_snapshots=self.leaderboard_snapshots
        )
        
        with open("game_log.json", "w") as f:
            json.dump(game_log.__dict__, f, indent=2, default=str)
        
        print(f"\n{'='*50}")
        print(f"GAME OVER! Winner: {winner}")
        print(f"Final log written to game_log.json")
        print(f"{'='*50}\n")


def print_phase_header(day: int, phase: str):
    print(f"\n{'='*20} Day {day} ({phase}) {'='*20}")


def print_moderation(speaker: str, decision: str, reason: str):
    print(f"[Overseer moderation] Speaker={speaker}, decision={decision}, reason={reason}")


def print_vote(voter: str, target: str):
    print(f"[Vote] {voter} -> {target}")


def print_exclusion(player: str):
    print(f"[Excluded] {player}")


def print_night_kill(player: str):
    print(f"[Night kill] {player}")


def print_leaderboard(leaderboard: Any):
    scores_str = ", ".join([f"{e.player}:{e.suspicion:.2f}" for e in leaderboard.scores])
    print(f"[Overseer leaderboard] scores=[{scores_str}], top_guess={leaderboard.top_guess}")


def print_fortune_teller_result(teller: str, target: str, role: str):
    print(f"[Fortune Teller] {teller} inspected {target} (result kept private)")


def print_final_reveal(players: List[PlayerState]):
    print("\n=== FINAL ROLE REVEAL ===")
    for p in players:
        status = "ALIVE" if p.alive else "DEAD"
        print(f"  {p.name}: {p.role.value} ({status})")
    print()