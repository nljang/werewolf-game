#!/usr/bin/env python3
"""
Experiment 1 - Part 2: Truncation Experiment

Tests H4: Truncating CoT improves Overseer accuracy

Method:
- For each game, create 4 variants with truncated CoT: 25%, 50%, 75%, 100%
- Re-run Overseer with each variant
- Compare accuracy across truncation levels
- Expect: Less CoT → Better accuracy (especially for catching werewolves)

Author: Research team
"""

import json
import sys
import os
import subprocess
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any
from scipy import stats

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_game_data(game_file: Path) -> Dict[str, Any]:
    """Load a game result file."""
    with open(game_file, 'r') as f:
        return json.load(f)


def truncate_cot(cot_text: str, fraction: float) -> str:
    """
    Truncate CoT to specified fraction of sentences.

    Args:
        cot_text: Full CoT text (sentences separated by newlines or periods)
        fraction: Fraction to keep (0.25, 0.50, 0.75, 1.0)

    Returns:
        Truncated CoT text
    """
    if fraction >= 1.0:
        return cot_text

    # Split into sentences (simple approach)
    sentences = [s.strip() for s in cot_text.split('\n\n') if s.strip()]

    if not sentences:
        return cot_text

    # Keep first N sentences
    n_keep = max(1, int(len(sentences) * fraction))
    return '\n\n'.join(sentences[:n_keep])


def create_truncated_game_variant(game_data: Dict, fraction: float, output_dir: Path) -> Path:
    """
    Create a truncated variant of a game with specified CoT fraction.

    Returns path to variant game file.
    """
    variant = game_data.copy()
    variant['truncation_fraction'] = fraction

    # Truncate each player's CoT
    for player_name, player_info in variant['players'].items():
        if 'cot' in player_info:
            player_info['cot'] = truncate_cot(player_info['cot'], fraction)

    # Save variant
    game_id = variant['game_id']
    seed = variant['seed']
    variant_file = output_dir / f"game_{seed}_truncated_{int(fraction*100)}.json"

    with open(variant_file, 'w') as f:
        json.dump(variant, f, indent=2)

    return variant_file


def run_overseer_on_variant(variant_file: Path, api_key: str) -> Dict[str, Any]:
    """
    Run Overseer on a truncated game variant.

    This is a simulation - in reality you'd re-run the overseer logic.
    For now, we'll create a placeholder that you can replace with actual overseer call.
    """

    # TODO: Implement actual overseer re-run
    # For now, return placeholder results

    with open(variant_file, 'r') as f:
        game_data = json.load(f)

    # Placeholder: Random guess (replace with actual overseer)
    import random
    random.seed(game_data['seed'] + int(game_data['truncation_fraction'] * 100))

    players = list(game_data['players'].keys())
    overseer_guess = random.choice(players)
    ground_truth = game_data['ground_truth']

    return {
        'game_id': game_data['game_id'],
        'seed': game_data['seed'],
        'truncation_fraction': game_data['truncation_fraction'],
        'overseer_guess': overseer_guess,
        'ground_truth': ground_truth,
        'correct': overseer_guess == ground_truth
    }


def run_truncation_experiment(game_files: List[Path], fractions: List[float],
                               output_dir: Path, api_key: str) -> pd.DataFrame:
    """
    Run truncation experiment across all games and fractions.

    Args:
        game_files: List of original game files
        fractions: List of truncation fractions to test (e.g., [0.25, 0.50, 0.75, 1.0])
        output_dir: Directory to save variants and results
        api_key: Anthropic API key for overseer

    Returns:
        DataFrame with results for each (game, fraction) combination
    """

    output_dir.mkdir(exist_ok=True, parents=True)
    variants_dir = output_dir / 'truncated_variants'
    variants_dir.mkdir(exist_ok=True)

    results = []

    print(f"\n🔬 Running truncation experiment")
    print(f"   Games: {len(game_files)}")
    print(f"   Fractions: {fractions}")
    print(f"   Total runs: {len(game_files) * len(fractions)}\n")

    for i, game_file in enumerate(game_files, 1):
        game_data = load_game_data(game_file)
        seed = game_data['seed']

        print(f"[{i}/{len(game_files)}] Game {seed}")

        for fraction in fractions:
            print(f"   - Truncation {int(fraction*100)}%... ", end='', flush=True)

            # Create truncated variant
            variant_file = create_truncated_game_variant(game_data, fraction, variants_dir)

            # Run overseer on variant
            result = run_overseer_on_variant(variant_file, api_key)
            results.append(result)

            status = "✓" if result['correct'] else "✗"
            print(f"{status}")

            time.sleep(0.5)  # Brief delay

    return pd.DataFrame(results)


def analyze_truncation_results(results_df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze truncation experiment results.

    Tests H4: Does truncation improve accuracy?
    """

    analysis = {}

    # 1. Overall accuracy by truncation level
    accuracy_by_fraction = results_df.groupby('truncation_fraction')['correct'].mean()
    analysis['accuracy_by_fraction'] = accuracy_by_fraction

    # 2. Statistical test: 100% vs 25%
    full_correct = results_df[results_df['truncation_fraction'] == 1.0]['correct']
    truncated_correct = results_df[results_df['truncation_fraction'] == 0.25]['correct']

    # McNemar test (paired)
    # For each game: (correct_full, correct_truncated)
    paired_data = results_df.pivot(index='seed', columns='truncation_fraction', values='correct')

    if 1.0 in paired_data.columns and 0.25 in paired_data.columns:
        # Count discordant pairs
        full_correct_trunc_wrong = ((paired_data[1.0] == 1) & (paired_data[0.25] == 0)).sum()
        full_wrong_trunc_correct = ((paired_data[1.0] == 0) & (paired_data[0.25] == 1)).sum()

        # McNemar statistic
        if full_correct_trunc_wrong + full_wrong_trunc_correct > 0:
            mcnemar_stat = ((full_correct_trunc_wrong - full_wrong_trunc_correct) ** 2) / \
                           (full_correct_trunc_wrong + full_wrong_trunc_correct)
            mcnemar_p = 1 - stats.chi2.cdf(mcnemar_stat, df=1)
        else:
            mcnemar_stat = 0
            mcnemar_p = 1.0

        analysis['mcnemar_test'] = {
            'statistic': mcnemar_stat,
            'p_value': mcnemar_p,
            'full_correct_trunc_wrong': int(full_correct_trunc_wrong),
            'full_wrong_trunc_correct': int(full_wrong_trunc_correct)
        }

    # 3. Linear trend test
    # Treat fraction as continuous, test correlation with correctness
    corr, p_corr = stats.pearsonr(results_df['truncation_fraction'], results_df['correct'])
    analysis['trend_test'] = {
        'correlation': corr,
        'p_value': p_corr,
        'interpretation': 'Negative correlation = truncation helps' if corr < 0 else 'Positive correlation = truncation hurts'
    }

    return analysis


def plot_truncation_results(results_df: pd.DataFrame, analysis: Dict, output_dir: Path):
    """Generate plots for H4."""

    # Plot 1: Accuracy vs truncation level
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    accuracy_by_frac = analysis['accuracy_by_fraction']
    fractions = accuracy_by_frac.index * 100  # Convert to percentage
    accuracies = accuracy_by_frac.values

    ax.plot(fractions, accuracies, marker='o', markersize=10, linewidth=2, color='steelblue')
    ax.set_xlabel('CoT Kept (%)', fontsize=12)
    ax.set_ylabel('Overseer Accuracy', fontsize=12)
    ax.set_title('H4: Truncation Effect on Deception Detection', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 1)

    # Add reference line
    ax.axhline(y=0.2, color='red', linestyle='--', alpha=0.5, label='Random (20%)')
    ax.legend()

    # Annotate points
    for x, y in zip(fractions, accuracies):
        ax.annotate(f'{y:.1%}', xy=(x, y), xytext=(0, 10),
                    textcoords='offset points', ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_dir / 'h4_truncation_accuracy.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Plot 2: Per-game trajectories
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))

    for seed in results_df['seed'].unique():
        game_data = results_df[results_df['seed'] == seed]
        game_data = game_data.sort_values('truncation_fraction')
        ax.plot(game_data['truncation_fraction'] * 100, game_data['correct'],
                alpha=0.3, color='gray', linewidth=1)

    # Overlay mean
    ax.plot(fractions, accuracies, marker='o', markersize=10, linewidth=3,
            color='darkblue', label='Mean', zorder=10)

    ax.set_xlabel('CoT Kept (%)', fontsize=12)
    ax.set_ylabel('Correct (1) / Wrong (0)', fontsize=12)
    ax.set_title('Per-Game Truncation Trajectories', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'h4_truncation_trajectories.png', dpi=300, bbox_inches='tight')
    plt.close()


def generate_truncation_report(analysis: Dict, output_path: Path):
    """Generate markdown report for H4."""

    report = []
    report.append("# Experiment 1 - Part 2: Truncation Results (H4)\n")
    report.append("## Hypothesis\n")
    report.append("**H4**: Truncating CoT traces improves Overseer accuracy in deception detection\n")

    report.append("## Results\n")
    report.append("### Accuracy by Truncation Level\n")

    acc_df = pd.DataFrame({
        'CoT Kept (%)': [int(f*100) for f in analysis['accuracy_by_fraction'].index],
        'Accuracy': [f"{v:.1%}" for v in analysis['accuracy_by_fraction'].values]
    })
    report.append(acc_df.to_markdown(index=False))
    report.append("\n")

    if 'mcnemar_test' in analysis:
        mcnemar = analysis['mcnemar_test']
        report.append("### Statistical Test: 100% vs 25%\n")
        report.append(f"**McNemar's Test** (paired comparison):")
        report.append(f"- Full correct, truncated wrong: {mcnemar['full_correct_trunc_wrong']}")
        report.append(f"- Full wrong, truncated correct: {mcnemar['full_wrong_trunc_correct']}")
        report.append(f"- χ² = {mcnemar['statistic']:.3f}, p = {mcnemar['p_value']:.3f}")
        report.append(f"- **Conclusion**: {'✅ SIGNIFICANT' if mcnemar['p_value'] < 0.05 else '⚠️ NOT SIGNIFICANT'}\n")

    trend = analysis['trend_test']
    report.append("### Trend Analysis\n")
    report.append(f"**Correlation** between truncation level and correctness:")
    report.append(f"- r = {trend['correlation']:.3f}, p = {trend['p_value']:.3f}")
    report.append(f"- {trend['interpretation']}")
    report.append(f"- **Conclusion**: {'✅ H4 SUPPORTED' if trend['correlation'] < 0 and trend['p_value'] < 0.05 else '❌ H4 NOT SUPPORTED'}\n")

    report.append("## Interpretation\n")
    report.append("See figures: h4_truncation_accuracy.png and h4_truncation_trajectories.png\n")

    with open(output_path, 'w') as f:
        f.write('\n'.join(report))


def main():
    """Run truncation experiment (H4)."""

    print("="*60)
    print("EXPERIMENT 1 - PART 2: TRUNCATION (H4)")
    print("="*60)

    # Configuration
    fractions = [0.25, 0.50, 0.75, 1.0]
    results_dir = Path(__file__).parent.parent / 'results'
    output_dir = Path(__file__).parent / 'experiment1_output'

    # Get API key
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("⚠️  Warning: ANTHROPIC_API_KEY not set")
        print("   Using placeholder results (random guesses)")
        print("   For real experiment, set API key and implement overseer re-run\n")

    # Load game files
    print("\n1. Loading game files...")
    game_files = sorted(results_dir.glob('game_*_filtered_cot.json'))
    print(f"   Found {len(game_files)} games")

    # Run experiment
    print("\n2. Running truncation experiment...")
    results_df = run_truncation_experiment(game_files, fractions, output_dir, api_key)
    print(f"\n   Completed {len(results_df)} runs")

    # Save raw results
    results_df.to_csv(output_dir / 'truncation_results.csv', index=False)

    # Analyze
    print("\n3. Analyzing results...")
    analysis = analyze_truncation_results(results_df)

    # Plot
    print("\n4. Generating plots...")
    plot_truncation_results(results_df, analysis, output_dir)

    # Report
    print("\n5. Generating report...")
    report_path = output_dir / 'EXPERIMENT1_H4_TRUNCATION_REPORT.md'
    generate_truncation_report(analysis, report_path)

    print("\n" + "="*60)
    print("TRUNCATION EXPERIMENT COMPLETE")
    print("="*60)
    print(f"\nResults saved to: {output_dir}/")
    print(f"Report: {report_path}")
    print("\n⚠️  NOTE: This used placeholder results (random guesses)")
    print("For real experiment, implement overseer re-run in run_overseer_on_variant()")


if __name__ == "__main__":
    main()
