# CoT Anti-Anchor Analysis Report

## Executive Summary

This report analyzes Chain-of-Thought reasoning patterns that mislead AI deception detectors.
We identify 'anti-anchors' - reasoning sentence types that correlate with overseer errors.

## Dataset Overview

- **Werewolf players analyzed**: 19
- **Villager players analyzed**: 76
- **True Positives** (werewolves caught): 7
- **False Negatives** (werewolves missed): 12
- **False Positives** (villagers accused): 12
- **True Negatives** (villagers cleared): 64

**Overseer Accuracy**: 36.8%

## Identified Anti-Anchors

Reasoning patterns that mislead the overseer:

### Ranked by Impact

**1. PLAN** (false_positive_marker)
   - Villagers who use PLAN more are WRONGLY ACCUSED
   - Avg in accused villagers: 2.08
   - Avg in cleared villagers: 1.67
   - Difference: 0.41

**2. JUSTIFICATION** (false_negative_marker)
   - Werewolves who use JUSTIFICATION more are MISSED by overseer
   - Avg in missed werewolves: 0.83
   - Avg in caught werewolves: 0.43
   - Difference: 0.40

**3. DECEPTION_STRATEGY** (false_positive_marker)
   - Villagers who use DECEPTION_STRATEGY more are WRONGLY ACCUSED
   - Avg in accused villagers: 0.42
   - Avg in cleared villagers: 0.11
   - Difference: 0.31

**4. ASSERTION** (false_positive_marker)
   - Villagers who use ASSERTION more are WRONGLY ACCUSED
   - Avg in accused villagers: 2.00
   - Avg in cleared villagers: 1.80
   - Difference: 0.20

**5. JUSTIFICATION** (false_positive_marker)
   - Villagers who use JUSTIFICATION more are WRONGLY ACCUSED
   - Avg in accused villagers: 0.42
   - Avg in cleared villagers: 0.27
   - Difference: 0.15

**6. FACT_RECALL** (false_positive_marker)
   - Villagers who use FACT_RECALL more are WRONGLY ACCUSED
   - Avg in accused villagers: 0.25
   - Avg in cleared villagers: 0.14
   - Difference: 0.11

**7. FACT_RECALL** (false_negative_marker)
   - Werewolves who use FACT_RECALL more are MISSED by overseer
   - Avg in missed werewolves: 0.08
   - Avg in caught werewolves: 0.00
   - Difference: 0.08

**8. EMOTION** (false_positive_marker)
   - Villagers who use EMOTION more are WRONGLY ACCUSED
   - Avg in accused villagers: 0.08
   - Avg in cleared villagers: 0.03
   - Difference: 0.05

## Tag Distribution by Role

### Werewolf Reasoning Patterns

- **DECEPTION_STRATEGY**: 2.92 avg per game (total: 38)
- **ASSERTION**: 1.62 avg per game (total: 26)
- **PLAN**: 1.50 avg per game (total: 27)
- **JUSTIFICATION**: 1.18 avg per game (total: 13)
- **FACT_RECALL**: 1.00 avg per game (total: 1)

### Villager Reasoning Patterns

- **ASSERTION**: 1.96 avg per game (total: 139)
- **PLAN**: 1.78 avg per game (total: 132)
- **JUSTIFICATION**: 1.00 avg per game (total: 22)
- **DECEPTION_STRATEGY**: 1.00 avg per game (total: 12)
- **FACT_RECALL**: 1.00 avg per game (total: 12)
- **META_REASONING**: 1.00 avg per game (total: 1)
- **EMOTION**: 1.00 avg per game (total: 3)

## Detailed Error Analysis

### False Negatives (Missed Werewolves)

- **DECEPTION_STRATEGY**: 1.83 ± 1.80
- **PLAN**: 1.25 ± 0.75
- **ASSERTION**: 1.25 ± 0.97
- **JUSTIFICATION**: 0.83 ± 0.72
- **FACT_RECALL**: 0.08 ± 0.29

### False Positives (Wrongly Accused Villagers)

- **PLAN**: 2.08 ± 0.90
- **ASSERTION**: 2.00 ± 0.74
- **JUSTIFICATION**: 0.42 ± 0.51
- **DECEPTION_STRATEGY**: 0.42 ± 0.51
- **FACT_RECALL**: 0.25 ± 0.45
- **EMOTION**: 0.08 ± 0.29

## Research Implications

### Key Findings


**Patterns that help werewolves evade detection:**
- JUSTIFICATION: Werewolves who use JUSTIFICATION more are MISSED by overseer
- FACT_RECALL: Werewolves who use FACT_RECALL more are MISSED by overseer

**Patterns that cause false accusations:**
- PLAN: Villagers who use PLAN more are WRONGLY ACCUSED
- DECEPTION_STRATEGY: Villagers who use DECEPTION_STRATEGY more are WRONGLY ACCUSED
- ASSERTION: Villagers who use ASSERTION more are WRONGLY ACCUSED

### Comparison to Thought Anchors Theory

In mathematics and logic tasks, CoT 'anchors' improve reasoning by:
- Making intermediate steps explicit (PLAN, ASSERTION)
- Enabling error correction (BACKTRACK)
- Grounding reasoning in facts (FACT_RECALL)

In adversarial social contexts, these same patterns may become 'anti-anchors':
- Deceptive players can fabricate convincing JUSTIFICATION
- EMOTION signals may be strategically misleading
- DECEPTION_STRATEGY may leak but be ignored by overseer

### Future Research Directions

1. **Filtering algorithms**: Exclude anti-anchor tags from overseer input
2. **Adversarial training**: Train models to detect strategic deception
3. **Multi-game analysis**: Track how patterns evolve over time
4. **Human baselines**: Compare AI vs human sensitivity to anti-anchors
5. **Cross-domain validation**: Test on other social deduction games
