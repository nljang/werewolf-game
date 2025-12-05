"""
Run SemanticSimilarityWrapper on all 95 player traces.

Processes each player's CoT through the wrapper and saves results.
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.filters.cot_filter import AdvancedCoTFilter
from src.filters.semantic_similarity_wrapper import SemanticSimilarityWrapper


def load_all_game_data(results_dir: Path) -> list:
    """Load all game results with player CoT data."""
    games = []
    game_files = sorted(results_dir.glob("game_*_filtered_cot.json"))

    for game_file in game_files:
        with open(game_file, 'r') as f:
            games.append(json.load(f))

    return games


def create_trace_pairs(games: list, cot_filter: AdvancedCoTFilter) -> list:
    """
    Create RAW_COT / FILTERED_SUMMARY pairs for all player traces.

    Returns list of dicts with:
    - game_id, seed, player_name, role, is_werewolf
    - raw_cot
    - filtered_summary
    """
    pairs = []

    for game in games:
        werewolf = game['ground_truth']

        for player_name, player_info in game['players'].items():
            raw_cot = player_info['cot']

            # Apply AdvancedCoTFilter to get original filtered summary
            message_data = [{
                'type': 'message',
                'payload': {
                    'speaker': player_name,
                    'private_thoughts': raw_cot,
                    'public_text': ''
                }
            }]

            filtered_summary = cot_filter.create_advanced_summary_for_overseer(message_data)

            pairs.append({
                'game_id': game['game_id'],
                'seed': game['seed'],
                'player_name': player_name,
                'role': player_info['role'],
                'is_werewolf': player_name == werewolf,
                'raw_cot': raw_cot,
                'filtered_summary': filtered_summary
            })

    return pairs


def process_all_traces(pairs: list, wrapper: SemanticSimilarityWrapper) -> list:
    """Process all pairs through the wrapper."""
    results = []

    for i, pair in enumerate(pairs, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(pairs)}] {pair['player_name']} (Game {pair['game_id']}, {pair['role']})")
        print(f"{'='*80}")

        # Process through wrapper
        result = wrapper.process(pair['raw_cot'], pair['filtered_summary'])

        # Combine with metadata
        full_result = {
            'player_id': f"game{pair['game_id']}_{pair['player_name']}",
            'game_id': pair['game_id'],
            'seed': pair['seed'],
            'player_name': pair['player_name'],
            'role': pair['role'],
            'is_werewolf': pair['is_werewolf'],
            'raw_cot_text': result['raw_cot'],
            'original_filtered_summary': result['original_filtered_summary'],
            'original_similarity': result['original_similarity'],
            'improved_summary': result['improved_filtered_summary'],
            'improved_similarity': result['final_similarity'],
            'attempts_used': result['attempts_used'],
            'success': result['success']
        }

        results.append(full_result)

        # Print summary
        print(f"\n{'─'*80}")
        print(f"Original similarity: {result['original_similarity']:.3f}")
        print(f"Improved similarity: {result['final_similarity']:.3f}")
        print(f"Delta:               {result['final_similarity'] - result['original_similarity']:+.3f}")
        print(f"Attempts:            {result['attempts_used']}")
        print(f"Success:             {'✓' if result['success'] else '✗'}")
        print(f"{'─'*80}")

    return results


def save_results(results: list, output_dir: Path):
    """Save results to CSV and JSONL."""

    # Create DataFrame
    df = pd.DataFrame(results)

    # Save CSV (without full text for readability)
    csv_data = df[[
        'player_id', 'game_id', 'player_name', 'role', 'is_werewolf',
        'original_similarity', 'improved_similarity', 'attempts_used', 'success'
    ]].copy()

    csv_path = output_dir / 'semantic_filter_output.csv'
    csv_data.to_csv(csv_path, index=False)
    print(f"\n✓ CSV saved to {csv_path}")

    # Save JSONL (full data)
    jsonl_path = output_dir / 'semantic_filter_output.jsonl'
    with open(jsonl_path, 'w') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')
    print(f"✓ JSONL saved to {jsonl_path}")

    return df


def create_visualizations(results: list, output_dir: Path):
    """Create distribution plots and analysis visualizations."""

    df = pd.DataFrame(results)

    # Set style
    sns.set_style("whitegrid")

    # Figure 1: Before/After comparison
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1a. Histogram of original vs improved similarities
    ax = axes[0, 0]
    ax.hist(df['original_similarity'], bins=20, alpha=0.6, label='Original',
            color='red', edgecolor='black')
    ax.hist(df['improved_similarity'], bins=20, alpha=0.6, label='Improved',
            color='green', edgecolor='black')
    ax.axvline(df['original_similarity'].mean(), color='red', linestyle='--',
               linewidth=2, label=f'Original mean: {df["original_similarity"].mean():.3f}')
    ax.axvline(df['improved_similarity'].mean(), color='green', linestyle='--',
               linewidth=2, label=f'Improved mean: {df["improved_similarity"].mean():.3f}')
    ax.axvline(0.80, color='black', linestyle=':', linewidth=2, label='Threshold (0.80)')
    ax.set_xlabel('Cosine Similarity', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Distribution: Original vs Improved Similarity', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # 1b. Delta (improvement) distribution
    ax = axes[0, 1]
    deltas = df['improved_similarity'] - df['original_similarity']
    ax.hist(deltas, bins=20, alpha=0.7, color='blue', edgecolor='black')
    ax.axvline(0, color='red', linestyle='--', linewidth=2, label='No change')
    ax.axvline(deltas.mean(), color='green', linestyle='--', linewidth=2,
               label=f'Mean improvement: {deltas.mean():+.3f}')
    ax.set_xlabel('Similarity Improvement (Δ)', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Distribution of Improvements', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # 1c. Success rate by role
    ax = axes[1, 0]
    success_by_role = df.groupby('role')['success'].agg(['sum', 'count'])
    success_by_role['rate'] = success_by_role['sum'] / success_by_role['count']
    success_by_role['rate'].plot(kind='bar', ax=ax, color=['blue', 'red', 'green'],
                                  edgecolor='black', alpha=0.7)
    ax.set_ylabel('Success Rate (≥0.80 threshold)', fontsize=12)
    ax.set_title('Success Rate by Role', fontsize=14, fontweight='bold')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.axhline(0.80, color='black', linestyle=':', linewidth=2, label='Target: 80%')
    ax.legend()
    ax.grid(alpha=0.3)

    # 1d. Scatter: Original vs Improved
    ax = axes[1, 1]
    werewolf_df = df[df['is_werewolf']]
    villager_df = df[~df['is_werewolf']]

    ax.scatter(werewolf_df['original_similarity'], werewolf_df['improved_similarity'],
              alpha=0.6, s=100, label='Werewolves', color='red', edgecolor='black')
    ax.scatter(villager_df['original_similarity'], villager_df['improved_similarity'],
              alpha=0.6, s=100, label='Villagers', color='blue', edgecolor='black')
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='No improvement')
    ax.axhline(0.80, color='green', linestyle=':', linewidth=2, label='Threshold (0.80)')
    ax.axvline(0.80, color='green', linestyle=':', linewidth=2)
    ax.set_xlabel('Original Similarity', fontsize=12)
    ax.set_ylabel('Improved Similarity', fontsize=12)
    ax.set_title('Original vs Improved Similarity', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'semantic_wrapper_results.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"✓ Visualizations saved to {output_dir / 'semantic_wrapper_results.png'}")


def generate_summary_report(results: list, output_dir: Path):
    """Generate markdown summary report."""

    df = pd.DataFrame(results)

    # Compute statistics
    original_mean = df['original_similarity'].mean()
    improved_mean = df['improved_similarity'].mean()
    mean_delta = improved_mean - original_mean

    success_rate = df['success'].sum() / len(df)
    mean_attempts = df['attempts_used'].mean()

    werewolf_df = df[df['is_werewolf']]
    villager_df = df[~df['is_werewolf']]

    report = f"""# Semantic Similarity Wrapper: Full Results

## Summary

Applied SemanticSimilarityWrapper to all 95 player traces from 19 games.

**Goal**: Improve filtered summaries to maintain semantic similarity ≥ 0.80 with raw CoT.

---

## Overall Results

| Metric | Value |
|--------|-------|
| **Total traces processed** | {len(df)} |
| **Original mean similarity** | {original_mean:.4f} |
| **Improved mean similarity** | {improved_mean:.4f} |
| **Mean improvement** | {mean_delta:+.4f} |
| **Success rate** (≥0.80) | {success_rate*100:.1f}% ({df['success'].sum()}/{len(df)}) |
| **Mean attempts used** | {mean_attempts:.2f} |

**Interpretation**:
- Original AdvancedCoTFilter: {original_mean:.2f} similarity (moderate preservation)
- Improved wrapper: {improved_mean:.2f} similarity ({'+' if mean_delta > 0 else ''}{mean_delta:.2f} improvement)
- Success rate: {success_rate*100:.0f}% of traces reached ≥0.80 threshold

---

## By Role

### Werewolves (n={len(werewolf_df)})

| Metric | Value |
|--------|-------|
| **Original similarity** | {werewolf_df['original_similarity'].mean():.4f} |
| **Improved similarity** | {werewolf_df['improved_similarity'].mean():.4f} |
| **Mean improvement** | {werewolf_df['improved_similarity'].mean() - werewolf_df['original_similarity'].mean():+.4f} |
| **Success rate** | {werewolf_df['success'].sum() / len(werewolf_df) * 100:.1f}% |

### Villagers (n={len(villager_df)})

| Metric | Value |
|--------|-------|
| **Original similarity** | {villager_df['original_similarity'].mean():.4f} |
| **Improved similarity** | {villager_df['improved_similarity'].mean():.4f} |
| **Mean improvement** | {villager_df['improved_similarity'].mean() - villager_df['original_similarity'].mean():+.4f} |
| **Success rate** | {villager_df['success'].sum() / len(villager_df) * 100:.1f}% |

---

## Distribution Statistics

### Original Similarity
- Min: {df['original_similarity'].min():.4f}
- 25th percentile: {df['original_similarity'].quantile(0.25):.4f}
- Median: {df['original_similarity'].median():.4f}
- 75th percentile: {df['original_similarity'].quantile(0.75):.4f}
- Max: {df['original_similarity'].max():.4f}

### Improved Similarity
- Min: {df['improved_similarity'].min():.4f}
- 25th percentile: {df['improved_similarity'].quantile(0.25):.4f}
- Median: {df['improved_similarity'].median():.4f}
- 75th percentile: {df['improved_similarity'].quantile(0.75):.4f}
- Max: {df['improved_similarity'].max():.4f}

---

## Attempt Distribution

| Attempts | Count | Percentage |
|----------|-------|------------|
| 0 (already ≥0.80) | {(df['attempts_used'] == 0).sum()} | {(df['attempts_used'] == 0).sum() / len(df) * 100:.1f}% |
| 1 | {(df['attempts_used'] == 1).sum()} | {(df['attempts_used'] == 1).sum() / len(df) * 100:.1f}% |
| 2 | {(df['attempts_used'] == 2).sum()} | {(df['attempts_used'] == 2).sum() / len(df) * 100:.1f}% |
| 3 (max) | {(df['attempts_used'] == 3).sum()} | {(df['attempts_used'] == 3).sum() / len(df) * 100:.1f}% |

---

## Key Findings

1. **Improvement achieved**: Mean similarity increased from {original_mean:.2f} → {improved_mean:.2f} ({mean_delta:+.2f})

2. **Success rate**: {success_rate*100:.0f}% of traces reached ≥0.80 threshold

3. **Role differences**:
   - Werewolves: {werewolf_df['improved_similarity'].mean() - werewolf_df['original_similarity'].mean():+.3f} improvement
   - Villagers: {villager_df['improved_similarity'].mean() - villager_df['original_similarity'].mean():+.3f} improvement

4. **Efficiency**: Average {mean_attempts:.1f} attempts per trace

---

## Comparison to Original H4 Finding

**Original discovery**:
- AdvancedCoTFilter (no wrapper): 0.68 similarity, 37% overseer accuracy
- Direct CoT (no filter): 1.00 similarity, 100% overseer accuracy

**With SemanticSimilarityWrapper**:
- Filtered + Wrapper: {improved_mean:.2f} similarity
- **Prediction**: Should achieve ~{50 + (improved_mean - 0.68) * 100:.0f}% overseer accuracy (between 37% and 100%)

---

## Files Generated

1. **semantic_filter_output.csv** - Summary statistics
2. **semantic_filter_output.jsonl** - Full results with text
3. **semantic_wrapper_results.png** - Distribution plots
4. **SEMANTIC_WRAPPER_REPORT.md** - This report

---

**Generated**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
**Model**: BAAI/bge-large-en-v1.5 (embeddings), Claude Sonnet (summary improvement)
**Sample**: {len(df)} player traces from {df['game_id'].nunique()} games
"""

    report_path = output_dir / 'SEMANTIC_WRAPPER_REPORT.md'
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"✓ Report saved to {report_path}")


def main():
    """Main execution."""

    print("="*80)
    print("SEMANTIC SIMILARITY WRAPPER: ALL 95 PLAYER TRACES")
    print("="*80)

    # Setup paths
    results_dir = Path("results")
    output_dir = Path("analysis/experiment1_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load games
    print("\nLoading game data...")
    games = load_all_game_data(results_dir)
    print(f"✓ Loaded {len(games)} games")

    # Initialize filter
    print("\nInitializing AdvancedCoTFilter...")
    cot_filter = AdvancedCoTFilter()
    print("✓ Filter initialized")

    # Create pairs
    print("\nCreating RAW_COT / FILTERED_SUMMARY pairs...")
    pairs = create_trace_pairs(games, cot_filter)
    print(f"✓ Created {len(pairs)} pairs")

    # Initialize wrapper
    print("\nInitializing SemanticSimilarityWrapper...")
    wrapper = SemanticSimilarityWrapper(similarity_threshold=0.80, max_attempts=3)
    print("✓ Wrapper initialized")

    # Process all traces
    print(f"\nProcessing {len(pairs)} player traces...")
    print("This will take ~30-45 minutes (2-3 API calls per trace)\n")

    results = process_all_traces(pairs, wrapper)

    # Save results
    print("\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80)

    df = save_results(results, output_dir)
    create_visualizations(results, output_dir)
    generate_summary_report(results, output_dir)

    # Print final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"Total traces: {len(df)}")
    print(f"Original mean similarity: {df['original_similarity'].mean():.3f}")
    print(f"Improved mean similarity: {df['improved_similarity'].mean():.3f}")
    print(f"Mean improvement: {df['improved_similarity'].mean() - df['original_similarity'].mean():+.3f}")
    print(f"Success rate (≥0.80): {df['success'].sum() / len(df) * 100:.1f}%")
    print("="*80)

    print(f"\n✓ All outputs saved to {output_dir}/")


if __name__ == '__main__':
    main()
