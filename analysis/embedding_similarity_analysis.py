"""
Embedding Similarity Analysis: Raw CoT vs Filtered CoT

Compares embeddings to test if AdvancedCoTFilter destroys semantic structure.

Uses bge-large-en-v1.5 for high-quality embeddings.
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
import sys

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("ERROR: sentence-transformers not installed")
    print("Install with: pip install sentence-transformers")
    sys.exit(1)

# Import the filter
sys.path.append(str(Path(__file__).parent.parent))
from cot_filter import AdvancedCoTFilter


def load_game_data(results_dir: Path) -> List[Dict]:
    """Load all game results with CoT data."""
    games = []
    game_files = sorted(results_dir.glob("game_*_filtered_cot.json"))

    for game_file in game_files:
        with open(game_file, 'r') as f:
            games.append(json.load(f))

    return games


def apply_filter_to_cot(cot_text: str, filter_obj: AdvancedCoTFilter) -> str:
    """
    Apply AdvancedCoTFilter to CoT text.

    Returns the filtered summary that the original overseer would have seen.
    """
    # Convert CoT to message format expected by filter
    message_data = [{
        'type': 'message',
        'payload': {
            'speaker': 'Player',
            'private_thoughts': cot_text,
            'public_text': ''
        }
    }]

    # Generate filtered summary
    filtered_summary = filter_obj.create_advanced_summary_for_overseer(message_data)

    return filtered_summary


def compute_embeddings(texts: List[str], model: SentenceTransformer) -> np.ndarray:
    """Compute embeddings for a list of texts."""
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    return embeddings


def analyze_single_game(game_data: Dict, filter_obj: AdvancedCoTFilter,
                       model: SentenceTransformer) -> pd.DataFrame:
    """
    Analyze embedding similarity for all players in a single game.

    Returns DataFrame with columns:
    - player_name
    - role
    - is_werewolf
    - raw_cot
    - filtered_cot
    - raw_embedding
    - filtered_embedding
    - cosine_similarity
    """
    results = []

    werewolf = game_data['ground_truth']

    for player_name, player_info in game_data['players'].items():
        raw_cot = player_info['cot']

        # Apply filter
        filtered_cot = apply_filter_to_cot(raw_cot, filter_obj)

        # Compute embeddings
        raw_emb = model.encode(raw_cot, convert_to_numpy=True)
        filtered_emb = model.encode(filtered_cot, convert_to_numpy=True)

        # Compute cosine similarity
        similarity = cosine_similarity(
            raw_emb.reshape(1, -1),
            filtered_emb.reshape(1, -1)
        )[0, 0]

        results.append({
            'game_id': game_data['game_id'],
            'seed': game_data['seed'],
            'player_name': player_name,
            'role': player_info['role'],
            'is_werewolf': player_name == werewolf,
            'raw_cot': raw_cot,
            'filtered_cot': filtered_cot,
            'raw_cot_length': len(raw_cot),
            'filtered_cot_length': len(filtered_cot),
            'compression_ratio': len(filtered_cot) / len(raw_cot) if len(raw_cot) > 0 else 0,
            'raw_embedding': raw_emb,
            'filtered_embedding': filtered_emb,
            'cosine_similarity': similarity
        })

    return pd.DataFrame(results)


def create_visualizations(df: pd.DataFrame, output_dir: Path):
    """Create all visualization plots."""

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)

    # 1. Scatter plot: Raw vs Filtered similarity distribution
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1a. Histogram of cosine similarities
    ax = axes[0, 0]
    werewolf_sims = df[df['is_werewolf']]['cosine_similarity']
    villager_sims = df[~df['is_werewolf']]['cosine_similarity']

    ax.hist(werewolf_sims, bins=20, alpha=0.6, label='Werewolves', color='red', edgecolor='black')
    ax.hist(villager_sims, bins=20, alpha=0.6, label='Villagers', color='blue', edgecolor='black')
    ax.axvline(werewolf_sims.mean(), color='red', linestyle='--', linewidth=2, label=f'Werewolf mean: {werewolf_sims.mean():.3f}')
    ax.axvline(villager_sims.mean(), color='blue', linestyle='--', linewidth=2, label=f'Villager mean: {villager_sims.mean():.3f}')
    ax.set_xlabel('Cosine Similarity (Raw vs Filtered)', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title('Distribution of Raw-Filtered CoT Similarity', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # 1b. Compression ratio vs similarity
    ax = axes[0, 1]
    werewolf_df = df[df['is_werewolf']]
    villager_df = df[~df['is_werewolf']]

    ax.scatter(werewolf_df['compression_ratio'], werewolf_df['cosine_similarity'],
              alpha=0.6, s=100, label='Werewolves', color='red', edgecolor='black')
    ax.scatter(villager_df['compression_ratio'], villager_df['cosine_similarity'],
              alpha=0.6, s=100, label='Villagers', color='blue', edgecolor='black')
    ax.set_xlabel('Compression Ratio (Filtered/Raw length)', fontsize=12)
    ax.set_ylabel('Cosine Similarity', fontsize=12)
    ax.set_title('Compression vs Similarity', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # 1c. CoT length vs similarity
    ax = axes[1, 0]
    ax.scatter(werewolf_df['raw_cot_length'], werewolf_df['cosine_similarity'],
              alpha=0.6, s=100, label='Werewolves', color='red', edgecolor='black')
    ax.scatter(villager_df['raw_cot_length'], villager_df['cosine_similarity'],
              alpha=0.6, s=100, label='Villagers', color='blue', edgecolor='black')
    ax.set_xlabel('Raw CoT Length (chars)', fontsize=12)
    ax.set_ylabel('Cosine Similarity', fontsize=12)
    ax.set_title('CoT Length vs Embedding Similarity', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # 1d. Box plot comparison
    ax = axes[1, 1]
    data_to_plot = [werewolf_sims, villager_sims]
    bp = ax.boxplot(data_to_plot, labels=['Werewolves', 'Villagers'], patch_artist=True)
    bp['boxes'][0].set_facecolor('red')
    bp['boxes'][1].set_facecolor('blue')
    for patch in bp['boxes']:
        patch.set_alpha(0.6)
    ax.set_ylabel('Cosine Similarity', fontsize=12)
    ax.set_title('Similarity Distribution by Role', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'embedding_similarity_overview.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. t-SNE visualization
    print("\nGenerating t-SNE visualization...")

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Collect all embeddings
    raw_embeddings = np.stack(df['raw_embedding'].values)
    filtered_embeddings = np.stack(df['filtered_embedding'].values)

    # Combine for joint t-SNE
    all_embeddings = np.vstack([raw_embeddings, filtered_embeddings])

    # Run t-SNE
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(df) - 1))
    embeddings_2d = tsne.fit_transform(all_embeddings)

    # Split back
    raw_2d = embeddings_2d[:len(df)]
    filtered_2d = embeddings_2d[len(df):]

    # Plot raw embeddings
    ax = axes[0]
    werewolf_mask = df['is_werewolf'].values
    ax.scatter(raw_2d[~werewolf_mask, 0], raw_2d[~werewolf_mask, 1],
              alpha=0.6, s=100, label='Villagers', color='blue', edgecolor='black')
    ax.scatter(raw_2d[werewolf_mask, 0], raw_2d[werewolf_mask, 1],
              alpha=0.6, s=150, label='Werewolves', color='red', edgecolor='black', marker='^')
    ax.set_title('Raw CoT Embeddings (t-SNE)', fontsize=14, fontweight='bold')
    ax.legend()
    ax.set_xlabel('t-SNE 1')
    ax.set_ylabel('t-SNE 2')
    ax.grid(alpha=0.3)

    # Plot filtered embeddings
    ax = axes[1]
    ax.scatter(filtered_2d[~werewolf_mask, 0], filtered_2d[~werewolf_mask, 1],
              alpha=0.6, s=100, label='Villagers', color='blue', edgecolor='black')
    ax.scatter(filtered_2d[werewolf_mask, 0], filtered_2d[werewolf_mask, 1],
              alpha=0.6, s=150, label='Werewolves', color='red', edgecolor='black', marker='^')
    ax.set_title('Filtered CoT Embeddings (t-SNE)', fontsize=14, fontweight='bold')
    ax.legend()
    ax.set_xlabel('t-SNE 1')
    ax.set_ylabel('t-SNE 2')
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'embedding_tsne_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Paired trajectory plot (shows information loss per player)
    print("\nGenerating trajectory plot...")

    fig, ax = plt.subplots(figsize=(14, 8))

    for idx, row in df.iterrows():
        raw_pt = raw_2d[idx]
        filt_pt = filtered_2d[idx]

        color = 'red' if row['is_werewolf'] else 'blue'
        alpha = 0.3

        # Draw arrow from raw to filtered
        ax.annotate('', xy=filt_pt, xytext=raw_pt,
                   arrowprops=dict(arrowstyle='->', color=color, alpha=alpha, lw=1.5))

    # Plot points
    ax.scatter(raw_2d[~werewolf_mask, 0], raw_2d[~werewolf_mask, 1],
              alpha=0.7, s=120, label='Villagers (Raw)', color='blue', edgecolor='black', marker='o')
    ax.scatter(raw_2d[werewolf_mask, 0], raw_2d[werewolf_mask, 1],
              alpha=0.7, s=150, label='Werewolves (Raw)', color='red', edgecolor='black', marker='^')

    ax.scatter(filtered_2d[~werewolf_mask, 0], filtered_2d[~werewolf_mask, 1],
              alpha=0.7, s=120, label='Villagers (Filtered)', color='lightblue', edgecolor='black', marker='s')
    ax.scatter(filtered_2d[werewolf_mask, 0], filtered_2d[werewolf_mask, 1],
              alpha=0.7, s=150, label='Werewolves (Filtered)', color='lightcoral', edgecolor='black', marker='v')

    ax.set_title('Information Loss Trajectories: Raw → Filtered (t-SNE)', fontsize=14, fontweight='bold')
    ax.set_xlabel('t-SNE 1')
    ax.set_ylabel('t-SNE 2')
    ax.legend()
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'embedding_information_loss_trajectories.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"\n✓ Visualizations saved to {output_dir}/")


def generate_report(df: pd.DataFrame, output_path: Path):
    """Generate markdown report with statistical analysis."""

    werewolf_sims = df[df['is_werewolf']]['cosine_similarity']
    villager_sims = df[~df['is_werewolf']]['cosine_similarity']

    # Statistical tests
    from scipy import stats
    t_stat, p_value = stats.ttest_ind(werewolf_sims, villager_sims)

    report = f"""# Embedding Similarity Analysis: Raw vs Filtered CoT

## Summary

This analysis tests whether the AdvancedCoTFilter destroys semantic structure in Chain-of-Thought reasoning.

**Method**:
- Embedding model: `BAAI/bge-large-en-v1.5` (1024-dim)
- Metric: Cosine similarity between raw CoT and filtered CoT embeddings
- Sample: {len(df)} player traces ({len(werewolf_sims)} werewolves, {len(villager_sims)} villagers)

---

## Key Findings

### Overall Similarity

| Statistic | Value |
|-----------|-------|
| **Mean similarity** | {df['cosine_similarity'].mean():.4f} |
| **Median similarity** | {df['cosine_similarity'].median():.4f} |
| **Std deviation** | {df['cosine_similarity'].std():.4f} |
| **Min similarity** | {df['cosine_similarity'].min():.4f} |
| **Max similarity** | {df['cosine_similarity'].max():.4f} |

**Interpretation**:
- Similarity ranges from {df['cosine_similarity'].min():.2f} to {df['cosine_similarity'].max():.2f}
- Mean of {df['cosine_similarity'].mean():.2f} suggests {'moderate' if df['cosine_similarity'].mean() > 0.5 else 'low'} semantic preservation
- {'Filter preserves some semantic structure but loses significant information' if df['cosine_similarity'].mean() > 0.5 else 'Filter destroys semantic structure - embeddings are nearly orthogonal'}

---

### Werewolves vs Villagers

| Role | Mean Similarity | Std Dev | N |
|------|----------------|---------|---|
| **Werewolves** | {werewolf_sims.mean():.4f} | {werewolf_sims.std():.4f} | {len(werewolf_sims)} |
| **Villagers** | {villager_sims.mean():.4f} | {villager_sims.std():.4f} | {len(villager_sims)} |
| **Difference** | {werewolf_sims.mean() - villager_sims.mean():.4f} | - | - |

**Statistical Test** (Independent t-test):
- t-statistic: {t_stat:.4f}
- p-value: {p_value:.4f}
- **Conclusion**: {'✅ SIGNIFICANT difference' if p_value < 0.05 else '❌ NO significant difference'} (α=0.05)

**Interpretation**:
{f"Werewolf CoT loses MORE semantic information when filtered (lower similarity). This suggests the filter disproportionately destroys deceptive reasoning patterns." if werewolf_sims.mean() < villager_sims.mean() else "Villager CoT loses MORE semantic information when filtered (lower similarity). This suggests the filter disproportionately destroys innocent reasoning patterns." if werewolf_sims.mean() > villager_sims.mean() else "Filter affects both roles equally."}

---

### Compression Statistics

| Statistic | Value |
|-----------|-------|
| **Mean compression ratio** | {df['compression_ratio'].mean():.4f} |
| **Median compression ratio** | {df['compression_ratio'].median():.4f} |

**Information retention**: ~{df['compression_ratio'].mean() * 100:.1f}% of original character count

---

## Correlation Analysis

### Compression Ratio vs Similarity

```
Pearson r = {df['compression_ratio'].corr(df['cosine_similarity']):.4f}
```

**Interpretation**:
{f"Strong positive correlation - more compression reduces similarity more" if abs(df['compression_ratio'].corr(df['cosine_similarity'])) > 0.5 else "Weak correlation - compression ratio doesn't strongly predict similarity"}

### CoT Length vs Similarity

```
Pearson r = {df['raw_cot_length'].corr(df['cosine_similarity']):.4f}
```

**Interpretation**:
{f"Longer CoT loses more semantic information when filtered" if df['raw_cot_length'].corr(df['cosine_similarity']) < -0.3 else "CoT length doesn't strongly affect semantic preservation"}

---

## What This Means

### If Similarity is LOW (< 0.5):
✅ **Filter destroys semantic structure**
- Raw and filtered CoT are semantically different
- Embeddings are nearly orthogonal
- Overseer sees fundamentally different information

### If Similarity is HIGH (> 0.7):
⚠️ **Filter preserves structure but loses key tokens**
- Semantic structure mostly intact
- But specific deceptive phrases/patterns are removed
- Information loss is lexical, not semantic

### Our Result: {df['cosine_similarity'].mean():.2f}
{'✅ Filter destroys semantic structure (similarity < 0.5)' if df['cosine_similarity'].mean() < 0.5 else '⚠️ Filter preserves some structure but loses information (0.5 ≤ similarity < 0.7)' if df['cosine_similarity'].mean() < 0.7 else '❌ Filter preserves semantic structure (similarity ≥ 0.7)'}

---

## Implications for H4 Discovery

**H4 found**: Direct CoT (100% accuracy) vs Filtered CoT (37% accuracy)

**This embedding analysis shows**:
- Mean similarity: {df['cosine_similarity'].mean():.2f}
- Information loss: ~{(1 - df['cosine_similarity'].mean()) * 100:.0f}% semantic divergence
- {'High semantic divergence explains why filtered overseer fails' if df['cosine_similarity'].mean() < 0.5 else 'Moderate divergence suggests filter removes critical tokens while preserving general structure'}

**Conclusion**:
The filter {'destroys' if df['cosine_similarity'].mean() < 0.5 else 'significantly alters'} the semantic representation of CoT, which explains the 63 percentage point accuracy drop.

---

## Files Generated

1. **embedding_similarity_overview.png** - Main statistical plots
2. **embedding_tsne_comparison.png** - t-SNE visualization of raw vs filtered embeddings
3. **embedding_information_loss_trajectories.png** - Per-player information loss arrows
4. **embedding_similarity_analysis.csv** - Raw data
5. **EMBEDDING_SIMILARITY_REPORT.md** - This report

---

**Generated**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
**Model**: BAAI/bge-large-en-v1.5
**Sample size**: {len(df)} player traces across {df['game_id'].nunique()} games
"""

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"\n✓ Report saved to {output_path}")


def main():
    """Run embedding similarity analysis."""

    print("="*60)
    print("EMBEDDING SIMILARITY ANALYSIS: Raw vs Filtered CoT")
    print("="*60)

    # Setup paths
    results_dir = Path("results")
    output_dir = Path("analysis/experiment1_output")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load embedding model
    print("\nLoading embedding model (bge-large-en-v1.5)...")
    model = SentenceTransformer('BAAI/bge-large-en-v1.5')
    print("✓ Model loaded")

    # Initialize filter
    filter_obj = AdvancedCoTFilter()

    # Load games
    print("\nLoading game data...")
    games = load_game_data(results_dir)
    print(f"✓ Loaded {len(games)} games")

    # Analyze each game
    print("\nAnalyzing games...")
    all_results = []

    for i, game_data in enumerate(games, 1):
        print(f"  [{i}/{len(games)}] Game {game_data['game_id']}...")
        game_df = analyze_single_game(game_data, filter_obj, model)
        all_results.append(game_df)

    # Combine results
    df = pd.concat(all_results, ignore_index=True)

    # Save raw data
    csv_path = output_dir / 'embedding_similarity_analysis.csv'
    df_to_save = df.drop(columns=['raw_embedding', 'filtered_embedding'])  # Drop arrays for CSV
    df_to_save.to_csv(csv_path, index=False)
    print(f"\n✓ Raw data saved to {csv_path}")

    # Generate visualizations
    print("\nGenerating visualizations...")
    create_visualizations(df, output_dir)

    # Generate report
    print("\nGenerating report...")
    report_path = output_dir / 'EMBEDDING_SIMILARITY_REPORT.md'
    generate_report(df, report_path)

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total player traces analyzed: {len(df)}")
    print(f"  Werewolves: {df['is_werewolf'].sum()}")
    print(f"  Villagers: {(~df['is_werewolf']).sum()}")
    print(f"\nMean cosine similarity: {df['cosine_similarity'].mean():.4f}")
    print(f"  Werewolves: {df[df['is_werewolf']]['cosine_similarity'].mean():.4f}")
    print(f"  Villagers: {df[~df['is_werewolf']]['cosine_similarity'].mean():.4f}")
    print(f"\nMean compression ratio: {df['compression_ratio'].mean():.4f}")
    print(f"\nInterpretation: {'Filter DESTROYS semantic structure' if df['cosine_similarity'].mean() < 0.5 else 'Filter PRESERVES some structure but loses information' if df['cosine_similarity'].mean() < 0.7 else 'Filter preserves semantic structure'}")
    print("="*60)

    print(f"\n✓ All outputs saved to {output_dir}/")
    print("\nFiles created:")
    print("  - embedding_similarity_overview.png")
    print("  - embedding_tsne_comparison.png")
    print("  - embedding_information_loss_trajectories.png")
    print("  - embedding_similarity_analysis.csv")
    print("  - EMBEDDING_SIMILARITY_REPORT.md")


if __name__ == '__main__':
    main()
