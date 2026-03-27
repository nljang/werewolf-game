from dataclasses import dataclass


@dataclass
class GameConfig:
    # Game parameters
    n_players: int = 5
    n_werewolves: int = 1
    n_fortune_tellers: int = 1
    n_days_max: int = 3
    seed: int = 42

    # Agent LLM
    agent_model: str = "gpt-4o-mini"
    agent_provider: str = "openai"
    agent_temperature: float = 0.3

    # Overseer LLM
    overseer_model: str = "gpt-4o-mini"
    overseer_provider: str = "openai"
    overseer_temperature: float = 0.3

    # Overseer type: "filtered" | "direct_cot" | "no_cot"
    overseer_type: str = "filtered"

    # Werewolf evasion condition: "naive" | "coached" | "unconstrained"
    werewolf_condition: str = "coached"

    # API key env var names
    openai_api_key_env: str = "OPENAI_API_KEY"
    anthropic_api_key_env: str = "ANTHROPIC_API_KEY"

    # Legacy
    mock_llm: bool = False
