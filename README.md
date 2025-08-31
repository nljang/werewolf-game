# 🐺 AI-Powered Werewolf Game

A Python implementation of the classic social deduction game Werewolf (also known as Mafia) where AI language models play as both the players and the game moderator.

## Features

- **AI Players**: Each player is controlled by an LLM agent with distinct personalities and strategies
- **AI Overseer**: An AI moderator manages game flow, validates moves, and maintains fairness
- **Multiple LLM Providers**: Supports OpenAI GPT models and Anthropic Claude
- **Configurable Roles**: Villagers, Werewolves, and Fortune Tellers with authentic gameplay mechanics
- **Game Logging**: Comprehensive logging of all game events and player interactions
- **Deterministic Gameplay**: Seeded random generation for reproducible games

## Game Rules

- **Villagers** win by eliminating all werewolves
- **Werewolves** win by reducing villagers to equal or fewer numbers
- **Fortune Tellers** can investigate one player each night to learn their role
- Game alternates between day phases (discussion and voting) and night phases (special actions)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd custom_werewolf_game
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Usage

### Basic Game
```bash
python main.py
```

### Custom Configuration
```bash
python main.py --n-players 7 --n-werewolves 2 --n-fortune-tellers 1 --n-days-max 5
```

### Using Different Models
```bash
# Use different models for agents and overseer
python main.py --agent-model gpt-4o --overseer-model claude-3-sonnet --overseer-provider anthropic

# Mock LLM for testing
python main.py --mock-llm
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `--n-players` | 5 | Number of players in the game |
| `--n-werewolves` | 1 | Number of werewolf players |
| `--n-fortune-tellers` | 1 | Number of fortune teller players |
| `--n-days-max` | 3 | Maximum number of game days |
| `--seed` | 42 | Random seed for reproducible games |
| `--agent-model` | gpt-4o-mini | Model for player agents |
| `--agent-provider` | openai | Provider for agents (openai/anthropic/mock) |
| `--overseer-model` | gpt-4o-mini | Model for game overseer |
| `--overseer-provider` | openai | Provider for overseer (openai/anthropic/mock) |

## Environment Variables

Create a `.env` file with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Game Output

The game provides rich console output including:
- Phase transitions and game state
- Player messages and discussions
- Voting results and eliminations
- Night actions and results
- Final game outcome and player reveals

All game events are also logged to `game_log.json` for analysis.

## Architecture

- **`main.py`**: CLI entry point and configuration
- **`engine.py`**: Core game engine managing phases and state
- **`agents.py`**: AI agent implementations for players and overseer
- **`schemas.py`**: Data structures and enums for game state
- **`prompts.py`**: LLM prompts for different game scenarios
- **`llm.py`**: LLM provider abstraction layer
- **`config.py`**: Game configuration management
- **`logging_utils.py`**: Game logging and console output

## Requirements

- Python 3.7+
- OpenAI API key (for GPT models)
- Anthropic API key (for Claude models)
