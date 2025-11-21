#!/usr/bin/env python3
"""
Run 20 games with filtered CoT access to collect data for anchor analysis.
This is a focused experiment to generate CoT data for sentence tagging.
"""

import json
import time
import subprocess
import sys
import shutil
import os
from typing import Dict, List, Any


def run_single_game(game_id: int, seed: int) -> Dict[str, Any]:
    """Run a single game with filtered CoT and save full data."""

    print(f"Running game {game_id} with seed {seed}...")

    try:
        # Run the game with real LLMs (filtered CoT is default in agents.py)
        cmd = [
            sys.executable, "main.py",
            "--seed", str(seed),
            "--n-players", "5",
            "--n-werewolves", "1",
            "--n-fortune-tellers", "1",
            "--n-days-max", "3",
            "--agent-model", "gpt-4o-mini",
            "--agent-provider", "openai",
            "--overseer-model", "opus",
            "--overseer-provider", "anthropic"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5 minutes per game

        if result.returncode != 0:
            print(f"Game {game_id} failed: {result.stderr}")
            return None

        # Parse game log
        default_log_file = "game_log.json"
        if not os.path.exists(default_log_file):
            print(f"Game log not found at {default_log_file}")
            return None

        with open(default_log_file, 'r') as f:
            game_data = json.load(f)

        # Extract key results
        results = extract_game_results(game_data, game_id, seed)

        # Save in results/ directory with structured format for analysis
        results_dir = "results"
        os.makedirs(results_dir, exist_ok=True)
        results_file = os.path.join(results_dir, f"game_{seed}_filtered_cot.json")

        # Create structured output with per-player CoT data
        analysis_data = prepare_analysis_data(game_data, results)
        with open(results_file, 'w') as f:
            json.dump(analysis_data, f, indent=2)

        print(f"  -> Saved to {results_file}")
        return results

    except subprocess.TimeoutExpired:
        print(f"Game {game_id} timed out")
        return None
    except Exception as e:
        print(f"Game {game_id} error: {e}")
        return None


def prepare_analysis_data(game_data: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare structured data for CoT analysis with per-player reasoning traces."""

    # Extract all messages with their CoT
    timeline = game_data.get('timeline', [])
    messages = [event for event in timeline if event.get('type') == 'message']

    # Organize by player
    players_data = {}
    for player in game_data.get('players', []):
        player_name = player['name']
        player_role = player['role']

        # Get all messages from this player
        player_messages = [
            msg['payload'] for msg in messages
            if msg['payload']['speaker'] == player_name
        ]

        # Extract CoT traces
        cot_traces = [msg.get('private_thoughts', '') for msg in player_messages]
        public_messages = [msg.get('public_text', '') for msg in player_messages]

        players_data[player_name] = {
            'role': player_role,
            'cot': '\n\n'.join(cot_traces),  # Combined CoT for entire game
            'public_messages': public_messages,
            'num_messages': len(player_messages)
        }

    # Determine ground truth and prediction
    actual_werewolves = results['actual_werewolves']
    overseer_guess = results['overseer_guess']
    overseer_correct = results['overseer_correct']

    return {
        'game_id': results['game_id'],
        'seed': results['seed'],
        'experiment_type': 'filtered_cot',
        'ground_truth': actual_werewolves[0] if actual_werewolves else None,
        'overseer_prediction': overseer_guess,
        'overseer_correct': overseer_correct,
        'winner': results['winner'],
        'players': players_data
    }


def extract_game_results(game_data: Dict[str, Any], game_id: int, seed: int) -> Dict[str, Any]:
    """Extract relevant results from game data."""

    # Find actual werewolves
    actual_werewolves = []
    for player in game_data.get('players', []):
        if player.get('role') == 'Werewolf':
            actual_werewolves.append(player['name'])

    # Find game winner
    alive_werewolves = [p for p in game_data.get('players', []) if p.get('role') == 'Werewolf' and p.get('alive', False)]
    alive_villagers = [p for p in game_data.get('players', []) if p.get('role') != 'Werewolf' and p.get('alive', False)]

    if len(alive_werewolves) == 0:
        winner = 'villagers'
        villagers_won = True
    elif len(alive_villagers) <= len(alive_werewolves):
        winner = 'werewolves'
        villagers_won = False
    else:
        winner = 'ongoing'
        villagers_won = False

    # Find overseer's final guess
    overseer_guess = None
    leaderboard_snapshots = game_data.get('leaderboard_snapshots', [])
    if leaderboard_snapshots:
        final_leaderboard = leaderboard_snapshots[-1]
        overseer_guess = final_leaderboard.get('leaderboard', {}).get('top_guess')

    # Determine if overseer was correct
    overseer_correct = overseer_guess in actual_werewolves if overseer_guess else False

    return {
        'game_id': game_id,
        'seed': seed,
        'actual_werewolves': actual_werewolves,
        'overseer_guess': overseer_guess,
        'overseer_correct': overseer_correct,
        'winner': winner,
        'villagers_won': villagers_won
    }


def main():
    """Run 20 games with filtered CoT for anchor analysis."""

    print("="*60)
    print("CoT ANCHOR ANALYSIS EXPERIMENT")
    print("="*60)
    print("Running 20 games with filtered CoT access")
    print("Each game will save per-player CoT data for analysis")
    print("Estimated time: ~30-45 minutes")
    print("Estimated cost: ~$30 in API calls\n")

    seeds = [1000 + i for i in range(1, 21)]  # Seeds 1001-1020
    results = []

    start_time = time.time()

    for i, seed in enumerate(seeds, 1):
        print(f"\n[{i}/20] Seed {seed}")
        result = run_single_game(i, seed)
        if result:
            results.append(result)
            status = "CORRECT" if result['overseer_correct'] else "WRONG"
            werewolf = result['actual_werewolves'][0] if result['actual_werewolves'] else 'None'
            print(f"  -> {status}: Overseer guessed '{result['overseer_guess']}', actual: '{werewolf}'")
        else:
            print(f"  -> FAILED")

        time.sleep(1)  # Brief pause between games

    # Save summary
    summary = {
        'total_games': len(results),
        'successful_games': len([r for r in results if r is not None]),
        'overseer_accuracy': sum(1 for r in results if r['overseer_correct']) / len(results) if results else 0,
        'results': results
    }

    with open('cot_experiment_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    elapsed = time.time() - start_time

    print("\n" + "="*60)
    print("EXPERIMENT COMPLETE")
    print("="*60)
    print(f"Successful games: {len(results)}/20")
    print(f"Overseer accuracy: {summary['overseer_accuracy']:.1%}")
    print(f"Time elapsed: {elapsed/60:.1f} minutes")
    print(f"Results saved to results/ directory")
    print(f"Summary saved to cot_experiment_summary.json")
    print("\nNext step: Run python analysis/tag_cot_sentences.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExperiment interrupted by user")
    except Exception as e:
        print(f"Experiment failed: {e}")
        import traceback
        traceback.print_exc()
