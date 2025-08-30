#!/usr/bin/env python3

import click
import os
import sys
from dotenv import load_dotenv
from config import GameConfig
from engine import GameEngine
from llm import create_llm_provider


@click.command()
@click.option('--n-players', default=5, help='Number of players')
@click.option('--n-werewolves', default=1, help='Number of werewolves')
@click.option('--n-fortune-tellers', default=1, help='Number of fortune tellers')
@click.option('--n-days-max', default=3, help='Maximum number of days')
@click.option('--seed', default=42, help='Random seed for deterministic gameplay')

# Legacy options for backward compatibility
@click.option('--model', default=None, help='LLM model name (legacy - sets both agent and overseer)')
@click.option('--temperature', default=None, help='LLM temperature (legacy - sets both agent and overseer)')
@click.option('--mock-llm', is_flag=True, help='Use mock LLM for testing')
@click.option('--api-key-env', default='OPENAI_API_KEY', help='Environment variable for OpenAI API key')

# New dual-model options
@click.option('--agent-model', default='gpt-4o-mini', help='Model for player agents')
@click.option('--agent-provider', default='openai', help='Provider for agents (openai/anthropic/mock)')
@click.option('--agent-temperature', default=0.3, help='Temperature for player agents')

@click.option('--overseer-model', default='gpt-4o-mini', help='Model for overseer')
@click.option('--overseer-provider', default='openai', help='Provider for overseer (openai/anthropic/mock)')  
@click.option('--overseer-temperature', default=0.3, help='Temperature for overseer')

@click.option('--anthropic-api-key-env', default='ANTHROPIC_API_KEY', help='Environment variable for Anthropic API key')
def main(n_players, n_werewolves, n_fortune_tellers, n_days_max, seed, 
         model, temperature, mock_llm, api_key_env,
         agent_model, agent_provider, agent_temperature,
         overseer_model, overseer_provider, overseer_temperature,
         anthropic_api_key_env):
    """Run a simplified Werewolf game with LLM agents and an Overseer."""
    
    # Load environment variables
    load_dotenv()
    
    # Create config
    config = GameConfig(
        n_players=n_players,
        n_werewolves=n_werewolves,
        n_fortune_tellers=n_fortune_tellers,
        n_days_max=n_days_max,
        seed=seed,
        
        # New dual-model settings
        agent_model=agent_model,
        agent_provider=agent_provider,
        agent_temperature=agent_temperature,
        overseer_model=overseer_model,
        overseer_provider=overseer_provider,
        overseer_temperature=overseer_temperature,
        
        # API keys
        openai_api_key_env=api_key_env,
        anthropic_api_key_env=anthropic_api_key_env,
        
        # Legacy compatibility
        model_name=model,
        temperature=temperature,
        mock_llm=mock_llm
    )
    
    # Validate config
    try:
        config.validate()
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)
    
    # Create LLM providers
    try:
        agent_llm_provider = create_llm_provider(config, "agent")
        overseer_llm_provider = create_llm_provider(config, "overseer")
    except Exception as e:
        click.echo(f"Failed to create LLM providers: {e}", err=True)
        click.echo("Tip: Set OPENAI_API_KEY and/or ANTHROPIC_API_KEY environment variables or use --mock-llm flag", err=True)
        sys.exit(1)
    
    # Run game
    try:
        engine = GameEngine(config, agent_llm_provider, overseer_llm_provider)
        winner = engine.run()
        click.echo(f"\nGame completed successfully! Winner: {winner}")
    except KeyboardInterrupt:
        click.echo("\nGame interrupted by user", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Game error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()