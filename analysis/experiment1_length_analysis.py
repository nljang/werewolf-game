#!/usr/bin/env python3
"""
Experiment 1: CoT Length Analysis

Tests four hypotheses:
H1: Longer CoT traces reduce Overseer accuracy
H2: Length effect is stronger for werewolves than villagers
H3: Effect is mediated by JUSTIFICATION and PLAN counts
H4: Truncating CoT improves Overseer accuracy

Author: Research team
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Any
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)


def load_tagged_data(filepath: str) -> pd.DataFrame:
    """Load tagged CoT data and convert to player-level DataFrame."""

    data = []
    with open(filepath, 'r') as f:
        for line in f:
            data.append(json.loads(line))

    return pd.DataFrame(data)


def create_analysis_dataframe(tagged_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create analysis-ready DataFrame with all required features.

    Schema:
    - game_id, player_name, player_role
    - cot_length_sent: number of sentences
    - cot_length_tokens: approximate token count
    - justification_count, plan_count, assertion_count, etc.
    - overseer_guess, ground_truth
    - is_true_werewolf: 1 if this player is werewolf, else 0
    - overseer_correct_for_this_player: 1 if overseer correct about THIS player
    """

    rows = []

    for _, player in tagged_df.iterrows():
        # Count tags
        tag_counts = {}
        tagged_cot = player['tagged_cot']

        for sent in tagged_cot:
            tag = sent['tag']
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Compute lengths
        cot_length_sent = len(tagged_cot)
        cot_length_tokens = sum(len(sent['text'].split()) for sent in tagged_cot)

        # Determine correctness for this player
        is_true_werewolf = 1 if player['is_werewolf'] else 0
        was_predicted = 1 if player['was_predicted'] else 0

        # Overseer is "correct" about this player if:
        # - Player is werewolf AND was predicted (true positive)
        # - Player is not werewolf AND was not predicted (true negative)
        overseer_correct = int(is_true_werewolf == was_predicted)

        rows.append({
            'game_id': player['game_id'],
            'seed': player['seed'],
            'player_name': player['player_name'],
            'player_role': player['player_role'],
            'is_true_werewolf': is_true_werewolf,
            'was_predicted': was_predicted,
            'overseer_correct_for_this_player': overseer_correct,
            'ground_truth': player['ground_truth'],
            'overseer_prediction': player['overseer_prediction'],
            'overseer_correct_game': int(player['overseer_correct']),
            'cot_length_sent': cot_length_sent,
            'cot_length_tokens': cot_length_tokens,
            'justification_count': tag_counts.get('JUSTIFICATION', 0),
            'plan_count': tag_counts.get('PLAN', 0),
            'assertion_count': tag_counts.get('ASSERTION', 0),
            'deception_strategy_count': tag_counts.get('DECEPTION_STRATEGY', 0),
            'fact_recall_count': tag_counts.get('FACT_RECALL', 0),
            'emotion_count': tag_counts.get('EMOTION', 0),
            'meta_reasoning_count': tag_counts.get('META_REASONING', 0),
            'backtrack_count': tag_counts.get('BACKTRACK', 0),
        })

    return pd.DataFrame(rows)


def descriptive_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute descriptive statistics by role and outcome.

    Returns summary tables for paper/presentation.
    """

    results = {}

    # 1. Mean CoT length by role
    results['length_by_role'] = df.groupby('player_role').agg({
        'cot_length_sent': ['mean', 'std', 'min', 'max'],
        'cot_length_tokens': ['mean', 'std']
    }).round(2)

    # 2. For werewolves: caught vs missed
    werewolves = df[df['is_true_werewolf'] == 1].copy()
    werewolves['caught'] = werewolves['was_predicted']

    results['werewolf_by_outcome'] = werewolves.groupby('caught').agg({
        'cot_length_sent': ['mean', 'std'],
        'justification_count': ['mean', 'std'],
        'plan_count': ['mean', 'std'],
        'deception_strategy_count': ['mean', 'std']
    }).round(2)

    # 3. For villagers: accused vs cleared
    villagers = df[df['is_true_werewolf'] == 0].copy()
    villagers['accused'] = villagers['was_predicted']

    results['villager_by_outcome'] = villagers.groupby('accused').agg({
        'cot_length_sent': ['mean', 'std'],
        'justification_count': ['mean', 'std'],
        'plan_count': ['mean', 'std'],
        'assertion_count': ['mean', 'std']
    }).round(2)

    # 4. Overall correlation between length and tags
    results['length_tag_correlation'] = df[['cot_length_sent',
                                            'justification_count',
                                            'plan_count',
                                            'assertion_count']].corr().round(3)

    return results


def test_h1_h2_h3_regressions(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Test H1-H3 using logistic regression.

    H1: β_length < 0 (length hurts)
    H2: β_length×werewolf < 0 (length especially hurts werewolves)
    H3: Mediation by JUSTIFICATION/PLAN (coefficients shrink when added)
    """

    # Standardize continuous predictors
    df = df.copy()
    df['cot_length_z'] = (df['cot_length_sent'] - df['cot_length_sent'].mean()) / df['cot_length_sent'].std()
    df['justification_z'] = (df['justification_count'] - df['justification_count'].mean()) / (df['justification_count'].std() + 1e-10)
    df['plan_z'] = (df['plan_count'] - df['plan_count'].mean()) / (df['plan_count'].std() + 1e-10)

    results = {}

    # Model 1: Length + role + interaction (no mediators)
    formula1 = 'overseer_correct_for_this_player ~ cot_length_z + is_true_werewolf + cot_length_z:is_true_werewolf'
    model1 = smf.logit(formula1, data=df).fit(disp=False)
    results['model1'] = model1

    # Model 2: Add mediators (JUSTIFICATION, PLAN)
    formula2 = 'overseer_correct_for_this_player ~ cot_length_z + is_true_werewolf + cot_length_z:is_true_werewolf + justification_z + plan_z'
    model2 = smf.logit(formula2, data=df).fit(disp=False)
    results['model2'] = model2

    # Extract key coefficients for comparison
    results['h1_evidence'] = {
        'model1_beta_length': model1.params.get('cot_length_z', np.nan),
        'model1_p_length': model1.pvalues.get('cot_length_z', np.nan),
        'model2_beta_length': model2.params.get('cot_length_z', np.nan),
        'model2_p_length': model2.pvalues.get('cot_length_z', np.nan),
        'mediation_effect': model1.params.get('cot_length_z', 0) - model2.params.get('cot_length_z', 0)
    }

    results['h2_evidence'] = {
        'model1_beta_interaction': model1.params.get('cot_length_z:is_true_werewolf', np.nan),
        'model1_p_interaction': model1.pvalues.get('cot_length_z:is_true_werewolf', np.nan),
        'model2_beta_interaction': model2.params.get('cot_length_z:is_true_werewolf', np.nan),
        'model2_p_interaction': model2.pvalues.get('cot_length_z:is_true_werewolf', np.nan),
    }

    results['h3_evidence'] = {
        'beta_justification': model2.params.get('justification_z', np.nan),
        'p_justification': model2.pvalues.get('justification_z', np.nan),
        'beta_plan': model2.params.get('plan_z', np.nan),
        'p_plan': model2.pvalues.get('plan_z', np.nan),
        'length_shrinkage': (model1.params.get('cot_length_z', 0) - model2.params.get('cot_length_z', 0)) / (abs(model1.params.get('cot_length_z', 1)) + 1e-10)
    }

    return results


def plot_length_effects(df: pd.DataFrame, output_dir: Path):
    """Generate publication-quality plots for H1-H3."""

    output_dir.mkdir(exist_ok=True)

    # Plot 1: Accuracy vs CoT Length (binned)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Bin by quartiles (with duplicates='drop' to handle ties)
    try:
        df['length_quartile'] = pd.qcut(df['cot_length_sent'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'], duplicates='drop')
    except ValueError:
        # If still failing, use fewer bins
        df['length_quartile'] = pd.cut(df['cot_length_sent'], bins=3, labels=['Low', 'Med', 'High'])

    # Overall accuracy by quartile
    acc_by_quartile = df.groupby('length_quartile')['overseer_correct_for_this_player'].mean()
    ax1.bar(range(len(acc_by_quartile)), acc_by_quartile.values, alpha=0.7, color='steelblue')
    ax1.set_xticks(range(len(acc_by_quartile)))
    ax1.set_xticklabels(acc_by_quartile.index)
    ax1.set_ylabel('Overseer Accuracy (Player-Level)')
    ax1.set_xlabel('CoT Length Bin')
    ax1.set_title('H1: Longer CoT → Lower Accuracy')
    ax1.axhline(y=0.5, color='red', linestyle='--', alpha=0.5, label='Chance')
    ax1.legend()

    # By role
    for role in ['Werewolf', 'Villager', 'FortuneTeller']:
        role_df = df[df['player_role'] == role]
        if len(role_df) > 0 and 'length_quartile' in role_df.columns:
            acc_by_q = role_df.groupby('length_quartile')['overseer_correct_for_this_player'].mean()
            ax2.plot(range(len(acc_by_q)), acc_by_q.values, marker='o', label=role)

    ax2.set_xticks(range(len(acc_by_quartile)))
    ax2.set_xticklabels(acc_by_quartile.index)
    ax2.set_ylabel('Overseer Accuracy')
    ax2.set_xlabel('CoT Length Quartile')
    ax2.set_title('H2: Length Effect by Role')
    ax2.legend()
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / 'h1_h2_length_accuracy.png', dpi=300, bbox_inches='tight')
    plt.close()

    # Plot 2: Length vs Tag Counts (mediation visualization)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.scatter(df['cot_length_sent'], df['justification_count'], alpha=0.5, s=30)
    ax1.set_xlabel('CoT Length (sentences)')
    ax1.set_ylabel('JUSTIFICATION Count')
    ax1.set_title('H3 Mediation: Length → JUSTIFICATION')

    # Add regression line
    z = np.polyfit(df['cot_length_sent'], df['justification_count'], 1)
    p = np.poly1d(z)
    ax1.plot(df['cot_length_sent'].sort_values(), p(df['cot_length_sent'].sort_values()),
             "r--", alpha=0.8, linewidth=2)

    ax2.scatter(df['cot_length_sent'], df['plan_count'], alpha=0.5, s=30, color='orange')
    ax2.set_xlabel('CoT Length (sentences)')
    ax2.set_ylabel('PLAN Count')
    ax2.set_title('H3 Mediation: Length → PLAN')

    z = np.polyfit(df['cot_length_sent'], df['plan_count'], 1)
    p = np.poly1d(z)
    ax2.plot(df['cot_length_sent'].sort_values(), p(df['cot_length_sent'].sort_values()),
             "r--", alpha=0.8, linewidth=2)

    plt.tight_layout()
    plt.savefig(output_dir / 'h3_mediation_scatter.png', dpi=300, bbox_inches='tight')
    plt.close()


def generate_report(descriptive_results: Dict, regression_results: Dict, output_path: Path):
    """Generate comprehensive markdown report for H1-H3."""

    report = []
    report.append("# Experiment 1: CoT Length Analysis Results\n")
    report.append("## Hypotheses Tested\n")
    report.append("- **H1**: Longer CoT traces reduce Overseer accuracy")
    report.append("- **H2**: Length effect is stronger for werewolves than villagers")
    report.append("- **H3**: Effect is mediated by JUSTIFICATION and PLAN counts\n")

    report.append("## 1. Descriptive Statistics\n")
    report.append("### 1.1 CoT Length by Role\n")
    report.append(descriptive_results['length_by_role'].to_markdown())
    report.append("\n")

    report.append("### 1.2 Werewolves: Caught vs Missed\n")
    report.append(descriptive_results['werewolf_by_outcome'].to_markdown())
    report.append("\n")

    report.append("### 1.3 Villagers: Accused vs Cleared\n")
    report.append(descriptive_results['villager_by_outcome'].to_markdown())
    report.append("\n")

    report.append("### 1.4 Correlation: Length and Tag Counts\n")
    report.append(descriptive_results['length_tag_correlation'].to_markdown())
    report.append("\n")

    report.append("## 2. Regression Results\n")

    report.append("### Model 1: Length + Role + Interaction\n")
    report.append("```")
    report.append(str(regression_results['model1'].summary()))
    report.append("```\n")

    report.append("### Model 2: + JUSTIFICATION + PLAN (Mediators)\n")
    report.append("```")
    report.append(str(regression_results['model2'].summary()))
    report.append("```\n")

    report.append("## 3. Hypothesis Testing Results\n")

    h1 = regression_results['h1_evidence']
    report.append(f"### H1: Does length hurt overall?\n")
    report.append(f"- **Model 1** β_length = {h1['model1_beta_length']:.3f}, p = {h1['model1_p_length']:.3f}")
    report.append(f"- **Model 2** β_length = {h1['model2_beta_length']:.3f}, p = {h1['model2_p_length']:.3f}")
    report.append(f"- **Mediation effect**: {h1['mediation_effect']:.3f}")
    report.append(f"- **Conclusion**: {'✅ SUPPORTED' if h1['model1_beta_length'] < 0 else '❌ NOT SUPPORTED'}\n")

    h2 = regression_results['h2_evidence']
    report.append(f"### H2: Is length worse for werewolves?\n")
    report.append(f"- **Model 1** β_interaction = {h2['model1_beta_interaction']:.3f}, p = {h2['model1_p_interaction']:.3f}")
    report.append(f"- **Model 2** β_interaction = {h2['model2_beta_interaction']:.3f}, p = {h2['model2_p_interaction']:.3f}")
    report.append(f"- **Conclusion**: {'✅ SUPPORTED' if h2['model1_beta_interaction'] < 0 else '❌ NOT SUPPORTED'}\n")

    h3 = regression_results['h3_evidence']
    report.append(f"### H3: Is effect mediated by JUSTIFICATION/PLAN?\n")
    report.append(f"- **β_JUSTIFICATION** = {h3['beta_justification']:.3f}, p = {h3['p_justification']:.3f}")
    report.append(f"- **β_PLAN** = {h3['beta_plan']:.3f}, p = {h3['p_plan']:.3f}")
    report.append(f"- **Length coefficient shrinkage**: {h3['length_shrinkage']*100:.1f}%")
    report.append(f"- **Conclusion**: {'✅ SUPPORTED' if abs(h3['length_shrinkage']) > 0.2 else '⚠️ PARTIAL SUPPORT'}\n")

    report.append("## 4. Interpretation\n")
    report.append("TBD: Add interpretation based on results\n")

    with open(output_path, 'w') as f:
        f.write('\n'.join(report))


def main():
    """Run complete H1-H3 analysis on existing data."""

    print("="*60)
    print("EXPERIMENT 1: CoT LENGTH ANALYSIS (H1-H3)")
    print("="*60)

    # Load data
    print("\n1. Loading tagged CoT data...")
    tagged_file = Path(__file__).parent / 'tagged_cots.jsonl'
    tagged_df = load_tagged_data(str(tagged_file))
    print(f"   Loaded {len(tagged_df)} player traces")

    # Create analysis DataFrame
    print("\n2. Creating analysis DataFrame...")
    df = create_analysis_dataframe(tagged_df)
    print(f"   Analysis DataFrame: {len(df)} rows, {len(df.columns)} columns")

    # Descriptive analysis
    print("\n3. Running descriptive analysis...")
    descriptive_results = descriptive_analysis(df)
    print("   ✓ Computed summary statistics")

    # Regression analysis
    print("\n4. Running regression analysis (H1-H3)...")
    regression_results = test_h1_h2_h3_regressions(df)
    print("   ✓ Fit logistic regression models")

    # Generate plots
    print("\n5. Generating plots...")
    output_dir = Path(__file__).parent / 'experiment1_output'
    plot_length_effects(df, output_dir)
    print(f"   ✓ Saved plots to {output_dir}/")

    # Generate report
    print("\n6. Generating report...")
    report_path = output_dir / 'EXPERIMENT1_H1_H2_H3_REPORT.md'
    generate_report(descriptive_results, regression_results, report_path)
    print(f"   ✓ Saved report to {report_path}")

    # Save DataFrame for truncation experiment
    df_path = output_dir / 'analysis_dataframe.csv'
    df.to_csv(df_path, index=False)
    print(f"   ✓ Saved DataFrame to {df_path}")

    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print(f"\nNext step: Review {report_path}")
    print("Then run: python analysis/experiment1_truncation.py (for H4)")


if __name__ == "__main__":
    main()
