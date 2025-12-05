from dataclasses import dataclass
from typing import Optional


@dataclass
class GameConfig:
    n_players: int = 5
    n_werewolves: int = 1
    n_fortune_tellers: int = 1
    n_days_max: int = 3
    seed: int = 42
    
    # Agent (Player) LLM settings
    agent_model: str = "gpt-4o-mini"
    agent_provider: str = "openai"  # "openai", "anthropic", or "mock"
    agent_temperature: float = 0.3
    
    # Overseer LLM settings  
    overseer_model: str = "gpt-4o-mini"
    overseer_provider: str = "openai"  # "openai", "anthropic", or "mock"
    overseer_temperature: float = 0.3
    
    # API Keys
    openai_api_key_env: Optional[str] = "OPENAI_API_KEY"
    anthropic_api_key_env: Optional[str] = "ANTHROPIC_API_KEY"
    
    # Legacy compatibility
    model_name: Optional[str] = None  # For backward compatibility
    temperature: Optional[float] = None  # For backward compatibility
    mock_llm: bool = False
    
    def __post_init__(self):
        # Handle backward compatibility
        if self.model_name is not None:
            self.agent_model = self.model_name
            self.overseer_model = self.model_name
        if self.temperature is not None:
            self.agent_temperature = self.temperature
            self.overseer_temperature = self.temperature
        if self.mock_llm:
            self.agent_provider = "mock"
            self.overseer_provider = "mock"
    
    def validate(self):
        n_villagers = self.n_players - self.n_werewolves - self.n_fortune_tellers
        if n_villagers < 1:
            raise ValueError("Must have at least 1 villager")
        if self.n_werewolves < 1:
            raise ValueError("Must have at least 1 werewolf")
        if self.n_fortune_tellers < 0:
            raise ValueError("Cannot have negative fortune tellers")
        if self.n_players < 3:
            raise ValueError("Need at least 3 players for a game")