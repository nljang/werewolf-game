import argparse
import os
import sys

_core_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(os.path.dirname(_core_dir))
# engine.py uses flat imports (from schemas import) — needs src/core in path
# agents.py uses package imports (from src.core.schemas import) — needs repo root in path
for _p in (_core_dir, _repo_root):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from config import GameConfig
from engine import GameEngine
from llm import create_llm_provider


def main():
    parser = argparse.ArgumentParser(description="Run a Werewolf game")

    parser.add_argument("--n-players", type=int, default=5)
    parser.add_argument("--n-werewolves", type=int, default=1)
    parser.add_argument("--n-fortune-tellers", type=int, default=1)
    parser.add_argument("--n-days-max", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)

    parser.add_argument("--agent-model", type=str, default="gpt-4o-mini")
    parser.add_argument("--agent-provider", type=str, default="openai",
                        choices=["openai", "anthropic", "mock"])

    parser.add_argument("--overseer-model", type=str, default="gpt-4o-mini")
    parser.add_argument("--overseer-provider", type=str, default="openai",
                        choices=["openai", "anthropic", "mock"])
    parser.add_argument("--overseer-type", type=str, default="filtered",
                        choices=["filtered", "direct_cot", "no_cot"])

    parser.add_argument("--werewolf-condition", type=str, default="coached",
                        choices=["naive", "coached", "unconstrained"])

    parser.add_argument("--mock-llm", action="store_true",
                        help="Use mock LLM for both agents and overseer (for testing)")

    args = parser.parse_args()

    config = GameConfig(
        n_players=args.n_players,
        n_werewolves=args.n_werewolves,
        n_fortune_tellers=args.n_fortune_tellers,
        n_days_max=args.n_days_max,
        seed=args.seed,
        agent_model=args.agent_model,
        agent_provider="mock" if args.mock_llm else args.agent_provider,
        overseer_model=args.overseer_model,
        overseer_provider="mock" if args.mock_llm else args.overseer_provider,
        overseer_type=args.overseer_type,
        werewolf_condition=args.werewolf_condition,
        mock_llm=args.mock_llm,
    )

    agent_llm = create_llm_provider(config, "agent")
    overseer_llm = create_llm_provider(config, "overseer")

    engine = GameEngine(config, agent_llm, overseer_llm)
    engine.run()


if __name__ == "__main__":
    main()
