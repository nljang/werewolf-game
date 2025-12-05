import random
from typing import List, Dict, Any, Optional
from collections import Counter
from schemas import Role, Team, PlayerState, Message, Phase, Vote, ModerationAction
from agents import Player, Villager, Werewolf, FortuneTeller, Overseer
from logging_utils import (
    GameLogger, print_phase_header, print_moderation, print_vote,
    print_exclusion, print_night_kill, print_leaderboard,
    print_fortune_teller_result, print_final_reveal
)
from config import GameConfig


class GameEngine:
    def __init__(self, config: GameConfig, agent_llm_provider, overseer_llm_provider):
        self.config = config
        self.agent_llm = agent_llm_provider
        self.overseer_llm = overseer_llm_provider
        self.logger = GameLogger(config)
        self.day = 0
        
        # Set random seed for deterministic gameplay
        random.seed(config.seed)
        
        # Initialize players
        self.players_state: List[PlayerState] = self._initialize_players()
        self.players: Dict[str, Player] = self._create_player_agents()
        
        # Initialize overseer
        self.overseer = Overseer(overseer_llm_provider)
    
    def _initialize_players(self) -> List[PlayerState]:
        names = [f"Player{i+1}" for i in range(self.config.n_players)]
        random.shuffle(names)
        
        roles = (
            [Role.WEREWOLF] * self.config.n_werewolves +
            [Role.FORTUNE_TELLER] * self.config.n_fortune_tellers +
            [Role.VILLAGER] * (self.config.n_players - self.config.n_werewolves - self.config.n_fortune_tellers)
        )
        random.shuffle(roles)
        
        players = []
        for name, role in zip(names, roles):
            players.append(PlayerState(
                name=name,
                role=role,
                alive=True
            ))
        
        return players
    
    def _create_player_agents(self) -> Dict[str, Player]:
        agents = {}
        for state in self.players_state:
            if state.role == Role.VILLAGER:
                agents[state.name] = Villager(state, self.agent_llm)
            elif state.role == Role.WEREWOLF:
                agents[state.name] = Werewolf(state, self.agent_llm)
            elif state.role == Role.FORTUNE_TELLER:
                agents[state.name] = FortuneTeller(state, self.agent_llm)
        return agents
    
    def get_game_state(self) -> Dict[str, Any]:
        return {
            'players': self.players_state,
            'day': self.day
        }
    
    def get_alive_players(self) -> List[PlayerState]:
        return [p for p in self.players_state if p.alive]
    
    def check_victory(self) -> Optional[str]:
        alive = self.get_alive_players()
        werewolves = [p for p in alive if p.role == Role.WEREWOLF]
        villagers = [p for p in alive if p.role != Role.WEREWOLF]
        
        if len(werewolves) == 0:
            return Team.VILLAGERS.value
        elif len(werewolves) >= len(villagers):
            return Team.WEREWOLVES.value
        return None
    
    def day_phase(self):
        self.day += 1
        print_phase_header(self.day, "Daytime")
        
        game_state = self.get_game_state()
        alive_players = self.get_alive_players()
        
        # Day messages
        messages = []
        for player_state in alive_players:
            player = self.players[player_state.name]
            
            # Get player's message
            response = player.create_day_message(game_state)
            rationale = response.get("rationale", "No rationale")
            final_text = response.get("final", "I have nothing to say.")
            
            # Moderate the message
            moderation = self.overseer.moderate_message(
                player_state.name,
                Phase.DAY,
                rationale,
                final_text
            )
            
            print_moderation(player_state.name, moderation.action.value, moderation.reason)
            
            # Apply moderation
            if moderation.action == ModerationAction.VETO:
                public_text = "[Message removed by Overseer]"
            elif moderation.action == ModerationAction.REDACT:
                public_text = moderation.redacted_text or "[Redacted]"
            else:
                public_text = final_text
            
            # Create and store message
            message = Message(
                speaker=player_state.name,
                phase=Phase.DAY,
                public_text=public_text,
                private_thoughts=rationale,
                moderation=moderation
            )
            
            messages.append(message)
            self.logger.log_message(message)
            self.overseer.all_public_messages.append(message)
            
            # Share message with all players
            for other_player in self.players.values():
                other_player.message_history.append(message)
        
        # Voting phase
        print("\n[Voting Phase]")
        candidates = [p.name for p in alive_players]
        votes = []
        
        for player_state in alive_players:
            player = self.players[player_state.name]
            target = player.vote(candidates, game_state)
            vote = Vote(voter=player_state.name, target=target)
            votes.append(vote)
            
            print_vote(vote.voter, vote.target)
            self.logger.log_vote(vote)
            self.overseer.record_vote(vote.voter, vote.target)
        
        # Tally votes
        vote_counts = Counter([v.target for v in votes if v.target])
        
        if vote_counts:
            # Handle ties with random selection
            max_votes = max(vote_counts.values())
            tied_players = [p for p, count in vote_counts.items() if count == max_votes]
            excluded = random.choice(tied_players)
            
            # Exclude player
            excluded_player = next(p for p in self.players_state if p.name == excluded)
            excluded_player.alive = False
            
            print_exclusion(excluded)
            self.logger.log_event("exclusion", {"player": excluded, "votes": max_votes})
            self.overseer.record_event("exclusion", {"player": excluded})
        
        # Update leaderboard
        leaderboard = self.overseer.update_leaderboard(game_state)
        print_leaderboard(leaderboard)
        self.logger.log_leaderboard(self.day, "day", leaderboard)
    
    def night_phase(self):
        print_phase_header(self.day, "Night")
        
        game_state = self.get_game_state()
        alive_players = self.get_alive_players()
        
        # Werewolf elimination
        alive_werewolves = [p for p in alive_players if p.role == Role.WEREWOLF]
        if alive_werewolves:
            targets = []
            for wolf_state in alive_werewolves:
                wolf = self.players[wolf_state.name]
                target = wolf.night_action(game_state)
                if target:
                    targets.append(target)
            
            if targets:
                # Random tie-break for multiple wolf targets
                victim = random.choice(targets)
                victim_player = next(p for p in self.players_state if p.name == victim)
                victim_player.alive = False
                
                print_night_kill(victim)
                self.logger.log_event("night_kill", {"victim": victim})
                self.overseer.record_event("night_kill", {"victim": victim})
        
        # Fortune Teller inspection
        alive_fortune_tellers = [p for p in alive_players if p.role == Role.FORTUNE_TELLER]
        for ft_state in alive_fortune_tellers:
            ft = self.players[ft_state.name]
            target = ft.night_action(game_state)
            if target:
                target_player = next(p for p in self.players_state if p.name == target)
                print_fortune_teller_result(ft_state.name, target, target_player.role.value)
                self.logger.log_event("inspection", {
                    "fortune_teller": ft_state.name,
                    "target": target,
                    "role": target_player.role.value
                })
        
        # Update leaderboard after night
        leaderboard = self.overseer.update_leaderboard(game_state)
        print_leaderboard(leaderboard)
        self.logger.log_leaderboard(self.day, "night", leaderboard)
    
    def run(self) -> str:
        print("\n" + "="*50)
        print("WEREWOLF GAME STARTING")
        print(f"Players: {self.config.n_players}")
        print(f"Werewolves: {self.config.n_werewolves}")
        print(f"Fortune Tellers: {self.config.n_fortune_tellers}")
        print("="*50)
        
        # Game loop
        for _ in range(self.config.n_days_max):
            # Day phase
            self.day_phase()
            
            # Check victory
            winner = self.check_victory()
            if winner:
                self._end_game(winner)
                return winner
            
            # Night phase
            self.night_phase()
            
            # Check victory
            winner = self.check_victory()
            if winner:
                self._end_game(winner)
                return winner
        
        # Max days reached - villagers win by default
        winner = Team.VILLAGERS.value
        self._end_game(winner)
        return winner
    
    def _end_game(self, winner: str):
        print_final_reveal(self.players_state)
        
        # Get final overseer guess
        final_leaderboard = self.overseer.update_leaderboard(self.get_game_state())
        print(f"Final Overseer Top Guess: {final_leaderboard.top_guess}")
        
        # Write final log
        self.logger.write_final_log(self.players_state, winner)