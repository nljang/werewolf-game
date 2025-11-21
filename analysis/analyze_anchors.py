#!/usr/bin/env python3
"""
Analyze tagged CoT sentences to identify "anti-anchors" - reasoning patterns
that mislead the Overseer in deception detection.

This script correlates sentence tags with overseer errors to determine which
types of reasoning are associated with false negatives (missing werewolves)
and false positives (accusing innocent players).
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Any
import statistics


def load_tagged_data(filepath: str) -> List[Dict[str, Any]]:
    """Load tagged CoT data from JSONL file."""
    data = []
    with open(filepath, 'r') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def extract_tag_frequencies(tagged_cot: List[Dict[str, str]]) -> Dict[str, int]:
    """Count frequency of each tag in a tagged CoT."""
    tags = [sent['tag'] for sent in tagged_cot]
    return dict(Counter(tags))


def analyze_by_role(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze tag distributions by player role."""

    werewolf_tags = []
    villager_tags = []

    for entry in data:
        role = entry['player_role']
        tag_freq = extract_tag_frequencies(entry['tagged_cot'])

        if 'Werewolf' in role:
            werewolf_tags.append(tag_freq)
        else:
            villager_tags.append(tag_freq)

    # Aggregate tag frequencies
    def aggregate_tags(tag_list):
        all_tags = defaultdict(list)
        for tag_freq in tag_list:
            for tag, count in tag_freq.items():
                all_tags[tag].append(count)

        # Calculate mean and std
        result = {}
        for tag, counts in all_tags.items():
            result[tag] = {
                'mean': statistics.mean(counts),
                'median': statistics.median(counts),
                'total': sum(counts),
                'occurrences': len(counts)
            }
        return result

    return {
        'werewolf_tags': aggregate_tags(werewolf_tags),
        'villager_tags': aggregate_tags(villager_tags),
        'num_werewolves': len(werewolf_tags),
        'num_villagers': len(villager_tags)
    }


def analyze_overseer_errors(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Identify tag patterns associated with overseer errors."""

    # Categorize players
    true_positives = []  # Werewolf correctly identified
    false_negatives = []  # Werewolf missed
    true_negatives = []  # Villager not accused
    false_positives = []  # Villager wrongly accused

    for entry in data:
        is_werewolf = entry['is_werewolf']
        was_predicted = entry['was_predicted']
        tag_freq = extract_tag_frequencies(entry['tagged_cot'])

        if is_werewolf and was_predicted:
            true_positives.append(tag_freq)
        elif is_werewolf and not was_predicted:
            false_negatives.append(tag_freq)
        elif not is_werewolf and not was_predicted:
            true_negatives.append(tag_freq)
        elif not is_werewolf and was_predicted:
            false_positives.append(tag_freq)

    def compute_tag_stats(tag_list, label):
        if not tag_list:
            return {}

        all_tags = defaultdict(list)
        for tag_freq in tag_list:
            # Get all possible tags
            for tag in ['PLAN', 'BACKTRACK', 'JUSTIFICATION', 'EMOTION',
                        'FACT_RECALL', 'ASSERTION', 'META_REASONING', 'DECEPTION_STRATEGY']:
                all_tags[tag].append(tag_freq.get(tag, 0))

        result = {}
        for tag, counts in all_tags.items():
            if sum(counts) > 0:  # Only include tags that appeared
                result[tag] = {
                    'mean': statistics.mean(counts),
                    'median': statistics.median(counts),
                    'stdev': statistics.stdev(counts) if len(counts) > 1 else 0,
                    'total': sum(counts)
                }
        return result

    return {
        'true_positives': {
            'count': len(true_positives),
            'tag_stats': compute_tag_stats(true_positives, 'TP')
        },
        'false_negatives': {
            'count': len(false_negatives),
            'tag_stats': compute_tag_stats(false_negatives, 'FN')
        },
        'true_negatives': {
            'count': len(true_negatives),
            'tag_stats': compute_tag_stats(true_negatives, 'TN')
        },
        'false_positives': {
            'count': len(false_positives),
            'tag_stats': compute_tag_stats(false_positives, 'FP')
        }
    }


def identify_anti_anchors(error_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Identify tags that are anti-anchors (mislead the overseer)."""

    anti_anchors = []

    # Compare false negatives vs true positives
    # Tags that appear MORE in FN than TP are anti-anchors for werewolves
    fn_tags = error_analysis['false_negatives']['tag_stats']
    tp_tags = error_analysis['true_positives']['tag_stats']

    for tag in fn_tags.keys():
        fn_mean = fn_tags[tag]['mean']
        tp_mean = tp_tags.get(tag, {}).get('mean', 0)

        if fn_mean > tp_mean:
            difference = fn_mean - tp_mean
            anti_anchors.append({
                'tag': tag,
                'type': 'false_negative_marker',
                'fn_mean': fn_mean,
                'tp_mean': tp_mean,
                'difference': difference,
                'interpretation': f"Werewolves who use {tag} more are MISSED by overseer"
            })

    # Compare false positives vs true negatives
    # Tags that appear MORE in FP than TN cause innocent players to be accused
    fp_tags = error_analysis['false_positives']['tag_stats']
    tn_tags = error_analysis['true_negatives']['tag_stats']

    for tag in fp_tags.keys():
        fp_mean = fp_tags[tag]['mean']
        tn_mean = tn_tags.get(tag, {}).get('mean', 0)

        if fp_mean > tn_mean:
            difference = fp_mean - tn_mean
            anti_anchors.append({
                'tag': tag,
                'type': 'false_positive_marker',
                'fp_mean': fp_mean,
                'tn_mean': tn_mean,
                'difference': difference,
                'interpretation': f"Villagers who use {tag} more are WRONGLY ACCUSED"
            })

    # Sort by difference
    anti_anchors.sort(key=lambda x: x['difference'], reverse=True)

    return anti_anchors


def generate_report(role_analysis: Dict, error_analysis: Dict, anti_anchors: List[Dict]) -> str:
    """Generate a comprehensive markdown report."""

    report = []
    report.append("# CoT Anti-Anchor Analysis Report")
    report.append("\n## Executive Summary\n")
    report.append("This report analyzes Chain-of-Thought reasoning patterns that mislead AI deception detectors.")
    report.append("We identify 'anti-anchors' - reasoning sentence types that correlate with overseer errors.\n")

    # Overview stats
    report.append("## Dataset Overview\n")
    report.append(f"- **Werewolf players analyzed**: {role_analysis['num_werewolves']}")
    report.append(f"- **Villager players analyzed**: {role_analysis['num_villagers']}")
    report.append(f"- **True Positives** (werewolves caught): {error_analysis['true_positives']['count']}")
    report.append(f"- **False Negatives** (werewolves missed): {error_analysis['false_negatives']['count']}")
    report.append(f"- **False Positives** (villagers accused): {error_analysis['false_positives']['count']}")
    report.append(f"- **True Negatives** (villagers cleared): {error_analysis['true_negatives']['count']}")

    # Accuracy
    tp = error_analysis['true_positives']['count']
    fn = error_analysis['false_negatives']['count']
    accuracy = tp / (tp + fn) if (tp + fn) > 0 else 0
    report.append(f"\n**Overseer Accuracy**: {accuracy:.1%}\n")

    # Anti-anchors
    report.append("## Identified Anti-Anchors\n")
    report.append("Reasoning patterns that mislead the overseer:\n")

    if not anti_anchors:
        report.append("*No significant anti-anchor patterns detected.*\n")
    else:
        report.append("### Ranked by Impact\n")
        for i, anchor in enumerate(anti_anchors[:10], 1):  # Top 10
            report.append(f"**{i}. {anchor['tag']}** ({anchor['type']})")
            report.append(f"   - {anchor['interpretation']}")
            if anchor['type'] == 'false_negative_marker':
                report.append(f"   - Avg in missed werewolves: {anchor['fn_mean']:.2f}")
                report.append(f"   - Avg in caught werewolves: {anchor['tp_mean']:.2f}")
            else:
                report.append(f"   - Avg in accused villagers: {anchor['fp_mean']:.2f}")
                report.append(f"   - Avg in cleared villagers: {anchor['tn_mean']:.2f}")
            report.append(f"   - Difference: {anchor['difference']:.2f}\n")

    # Tag distribution by role
    report.append("## Tag Distribution by Role\n")
    report.append("### Werewolf Reasoning Patterns\n")

    werewolf_tags = role_analysis['werewolf_tags']
    sorted_werewolf = sorted(werewolf_tags.items(), key=lambda x: x[1]['mean'], reverse=True)
    for tag, stats in sorted_werewolf:
        report.append(f"- **{tag}**: {stats['mean']:.2f} avg per game (total: {stats['total']})")

    report.append("\n### Villager Reasoning Patterns\n")
    villager_tags = role_analysis['villager_tags']
    sorted_villager = sorted(villager_tags.items(), key=lambda x: x[1]['mean'], reverse=True)
    for tag, stats in sorted_villager:
        report.append(f"- **{tag}**: {stats['mean']:.2f} avg per game (total: {stats['total']})")

    # Detailed error analysis
    report.append("\n## Detailed Error Analysis\n")

    report.append("### False Negatives (Missed Werewolves)\n")
    fn_stats = error_analysis['false_negatives']['tag_stats']
    if fn_stats:
        for tag, stats in sorted(fn_stats.items(), key=lambda x: x[1]['mean'], reverse=True):
            report.append(f"- **{tag}**: {stats['mean']:.2f} ± {stats['stdev']:.2f}")
    else:
        report.append("*No false negatives in dataset*\n")

    report.append("\n### False Positives (Wrongly Accused Villagers)\n")
    fp_stats = error_analysis['false_positives']['tag_stats']
    if fp_stats:
        for tag, stats in sorted(fp_stats.items(), key=lambda x: x[1]['mean'], reverse=True):
            report.append(f"- **{tag}**: {stats['mean']:.2f} ± {stats['stdev']:.2f}")
    else:
        report.append("*No false positives in dataset*\n")

    # Research implications
    report.append("\n## Research Implications\n")
    report.append("### Key Findings\n")

    if anti_anchors:
        fn_markers = [a for a in anti_anchors if a['type'] == 'false_negative_marker']
        fp_markers = [a for a in anti_anchors if a['type'] == 'false_positive_marker']

        if fn_markers:
            report.append("\n**Patterns that help werewolves evade detection:**")
            for anchor in fn_markers[:3]:
                report.append(f"- {anchor['tag']}: {anchor['interpretation']}")

        if fp_markers:
            report.append("\n**Patterns that cause false accusations:**")
            for anchor in fp_markers[:3]:
                report.append(f"- {anchor['tag']}: {anchor['interpretation']}")

    report.append("\n### Comparison to Thought Anchors Theory\n")
    report.append("In mathematics and logic tasks, CoT 'anchors' improve reasoning by:")
    report.append("- Making intermediate steps explicit (PLAN, ASSERTION)")
    report.append("- Enabling error correction (BACKTRACK)")
    report.append("- Grounding reasoning in facts (FACT_RECALL)\n")

    report.append("In adversarial social contexts, these same patterns may become 'anti-anchors':")
    report.append("- Deceptive players can fabricate convincing JUSTIFICATION")
    report.append("- EMOTION signals may be strategically misleading")
    report.append("- DECEPTION_STRATEGY may leak but be ignored by overseer\n")

    report.append("### Future Research Directions\n")
    report.append("1. **Filtering algorithms**: Exclude anti-anchor tags from overseer input")
    report.append("2. **Adversarial training**: Train models to detect strategic deception")
    report.append("3. **Multi-game analysis**: Track how patterns evolve over time")
    report.append("4. **Human baselines**: Compare AI vs human sensitivity to anti-anchors")
    report.append("5. **Cross-domain validation**: Test on other social deduction games\n")

    return "\n".join(report)


def main():
    """Main execution: analyze tagged CoT data."""

    print("="*60)
    print("ANTI-ANCHOR ANALYSIS")
    print("="*60)
    print("Analyzing CoT patterns that mislead the overseer\n")

    # Load tagged data
    tagged_file = Path(__file__).parent / 'tagged_cots.jsonl'
    if not tagged_file.exists():
        print(f"Error: {tagged_file} not found")
        print("Please run python analysis/tag_cot_sentences.py first")
        sys.exit(1)

    print(f"Loading tagged data from {tagged_file}...")
    data = load_tagged_data(str(tagged_file))
    print(f"Loaded {len(data)} player CoT traces\n")

    # Analyze by role
    print("Analyzing tag distributions by role...")
    role_analysis = analyze_by_role(data)

    # Analyze overseer errors
    print("Analyzing overseer error patterns...")
    error_analysis = analyze_overseer_errors(data)

    # Identify anti-anchors
    print("Identifying anti-anchor patterns...")
    anti_anchors = identify_anti_anchors(error_analysis)

    # Generate report
    print("Generating report...\n")
    report = generate_report(role_analysis, error_analysis, anti_anchors)

    # Save report
    report_file = Path(__file__).parent / 'ANTI_ANCHOR_REPORT.md'
    with open(report_file, 'w') as f:
        f.write(report)

    # Save raw analysis data
    analysis_file = Path(__file__).parent / 'anchor_analysis.json'
    with open(analysis_file, 'w') as f:
        json.dump({
            'role_analysis': role_analysis,
            'error_analysis': error_analysis,
            'anti_anchors': anti_anchors
        }, f, indent=2)

    print("="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print(f"Report saved to: {report_file}")
    print(f"Raw data saved to: {analysis_file}")
    print("\nTop 3 Anti-Anchors:")

    for i, anchor in enumerate(anti_anchors[:3], 1):
        print(f"{i}. {anchor['tag']} ({anchor['type']})")
        print(f"   {anchor['interpretation']}")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
