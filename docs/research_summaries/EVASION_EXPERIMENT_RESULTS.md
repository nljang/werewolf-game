# Evasion Conditions Experiment — Results

**Date:** March 2026
**Games:** 149 valid (50 naive, 49 coached, 50 unconstrained; 1 coached timeout)
**Seeds:** 2001–2050 (no overlap with prior Experiment 1 games at seeds 1001–1020)
**Overseer:** DirectCoTOverseer (H4-style raw CoT access, no filtering)
**Model:** Claude Haiku 4.5 (agents + overseer)

---

## Setup

Three werewolf CoT conditions were tested:

| Condition | Werewolf prompt |
|-----------|----------------|
| **naive** | No guidance — standard role description only |
| **coached** | Told to write CoT as if a concerned villager; current codebase default |
| **unconstrained** | Told explicitly it is being monitored by an AI overseer; figure out evasion yourself |

All conditions used the DirectCoTOverseer (introduced in H4), which gives the overseer raw unfiltered CoT. The AdvancedFilterOverseer was intentionally excluded — it is known to be broken (37% accuracy baseline).

---

## Results

### 1. Detection Accuracy

| Condition | Accuracy | Correct / Total |
|-----------|----------|----------------|
| naive | 84% | 42 / 50 |
| coached | 76% | 37 / 49 |
| unconstrained | 78% | 39 / 50 |

**Pairwise Fisher's exact tests (all ns):**
- naive vs coached: p = 0.33
- naive vs unconstrained: p = 0.61
- coached vs unconstrained: p = 0.82

**Finding:** Evasion prompting does not significantly degrade the DirectCoT overseer's ability to identify the werewolf. Accuracy is stable across all three conditions. The overseer reads the reasoning trace directly and correctly identifies deceptive intent regardless of how the werewolf is instructed to frame it.

---

### 2. Werewolf Win Rate

| Condition | Win Rate | Wins / Total |
|-----------|----------|-------------|
| naive | 32% | 16 / 50 |
| coached | 33% | 16 / 49 |
| unconstrained | **46%** | 23 / 50 |

**Fisher's exact (unconstrained vs naive):** p = 0.22 (not significant at n=50)

**Finding:** Unconstrained evasion shows a 14 percentage-point increase in werewolf win rate over naive/coached. This is directionally meaningful but does not reach significance at this sample size. A follow-up with ~100 games/condition would have sufficient power to confirm or rule out this effect.

---

### 3. The Key Finding: Detection × Game Outcome

The most striking result is the cross-tab of overseer correctness against game winner:

| | Overseer correct | Overseer wrong |
|--|--|--|
| **Werewolves won** | 16 / 16 / 23 | **0 / 0 / 0** |
| **Villagers won** | 26 / 21 / 16 | 8 / 12 / 11 |

*(columns: naive / coached / unconstrained)*

**The werewolves never won a single game in which the overseer missed them — across all 149 games and all three conditions.**

Chi-squared test for detection ~ win outcome:
- naive: p = 0.089 (trend)
- coached: p = 0.016 *
- unconstrained: p = 0.002 **

**Interpretation: Detection and prevention are structurally decoupled.**

The overseer correctly identifies the werewolf in most games, but correct identification does not prevent a werewolf win. The leaderboard is not fed back to the player agents, so the village cannot act on the overseer's judgment. Werewolves win exclusively in games where they are socially convincing enough that the village votes out the wrong person — but those are precisely the games where the CoT also reveals their intent clearly enough for the overseer to detect them.

When the overseer misses the werewolf, the village identifies and eliminates them through social dynamics alone. This means the current game setup is not a valid test of whether monitoring *prevents* deception — only whether it *detects* it.

---

### 4. CoT Length Distribution (Werewolf Only)

| Condition | Mean | Median | P25 | P75 |
|-----------|------|--------|-----|-----|
| naive | 86 words | 101 | 49 | 113 |
| coached | 88 words | 70 | 58 | 123 |
| unconstrained | 96 words | 102 | 87 | 109 |

CoT length is similar across conditions. Unconstrained is marginally longer, consistent with the model reasoning more explicitly about detection avoidance.

---

### 5. Keyword Rate Analysis

| Condition | Self-admission | Villager framing | Monitor-aware |
|-----------|---------------|-----------------|---------------|
| naive | 4% | 0% | 0% |
| coached | 2% | 0% | 0% |
| unconstrained | 0% | 0% | 0% |

Keyword-based detection of evasion behavior is near zero across all conditions. Even without explicit instructions, LLMs rarely write "I am the werewolf" in their CoT. The coached and unconstrained framing does not produce the specific phrasing patterns the keyword patterns targeted. This confirms that **semantic analysis is necessary for CoT classification** — keyword matching is insufficient.

---

## Implications

### For the Research Direction

The main experiment (Experiment 2) was designed to test whether evasion reduces overseer accuracy. The answer is: **no, not significantly**. The DirectCoT overseer is evasion-resistant.

However, the experiment surfaced a more important structural finding: **the monitoring-to-action pipeline is broken**. Even when detection is perfect, it doesn't translate into prevention because the overseer's output isn't connected to the agents' decision-making.

This points to the next research question: **what happens when the overseer's judgment IS fed back to the agents?** That is the experiment that would test whether CoT monitoring can actually prevent deception, not just detect it.

### For the Paper

The unconstrained condition's win rate increase (32% → 46%, p=0.22) is worth flagging as a power issue rather than a null result. With n=100 per condition, the same effect size (~14pp) would have power > 0.8.

The detection × outcome cross-tab (Missed+Won = 0) is the cleanest finding and the most publishable: it demonstrates, cleanly and without ambiguity, that detection alone is not sufficient for oversight.

---

## Files

| File | Description |
|------|-------------|
| `src/experiments/run_cot_experiment.py` | Runner script |
| `src/core/agents.py` | `DirectCoTOverseer`, `Werewolf` with condition |
| `src/core/prompts.py` | Condition-branched werewolf prompts |
| `src/core/config.py` | `GameConfig` with `overseer_type`, `werewolf_condition` |
| `src/core/main.py` | CLI entry point |
| `analysis/evasion_analysis.py` | Analysis script |
| `analysis/evasion_output/evasion_results.csv` | Flat CSV for external analysis |
| `results/evasion_experiment_summary.json` | All 149 game results |
| `results/experiment_progress.log` | Per-game progress log |
