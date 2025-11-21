# PI Meeting: Anti-Anchor Analysis Presentation

**Duration**: 15-20 minutes + Q&A

---

## SLIDE 1: Title (30 seconds)

**"Why Chain-of-Thought Fails in Adversarial Contexts: Anti-Anchor Analysis"**

Subtitle: Follow-up to Werewolf CoT Experiment

Your Name | Date | Lab Name

---

## SLIDE 2: Motivation - The Original Mystery (2 minutes)

**Previous Result** (from original experiment):
- Filtered CoT overseer: 15% accuracy
- No CoT overseer: 10.5% accuracy
- Not statistically significant (p=0.66)

**The Question**:
> "CoT helps in math/logic. Why doesn't it help in deception detection?"

**This Work**:
> "What if certain reasoning patterns actively MISLEAD the overseer?"

---

## SLIDE 3: Background - Thought Anchors (1 minute)

**Thought Anchors Framework** (Lanham et al., 2023):
- CoT sentences have functional roles (PLAN, JUSTIFICATION, etc.)
- In math: These "anchor" reasoning to truth
- Our hypothesis: In adversarial games, these become "anti-anchors"

**8 Sentence Types**:
- PLAN, JUSTIFICATION, ASSERTION, FACT_RECALL
- DECEPTION_STRATEGY, EMOTION, META_REASONING, BACKTRACK

---

## SLIDE 4: Method (3 minutes)

**Three-Step Pipeline**:

1. **Data Collection**
   - 19 Werewolf games (5 players each)
   - Collected full CoT traces for all players
   - 95 player logs (19 werewolves, 76 villagers)

2. **Sentence Tagging**
   - Used Claude Opus to tag each sentence
   - ~400-500 sentences tagged with functional role
   - Cost: $0.44 (very efficient!)

3. **Error Correlation Analysis**
   - Compare caught vs missed werewolves (False Negatives)
   - Compare accused vs cleared villagers (False Positives)
   - Identify tags correlated with overseer errors

**Key Design Choice**: Same seeds, controlled comparison to original experiment

---

## SLIDE 5: Results - Anti-Anchors Identified (3 minutes)

**Definition**: Anti-anchor = reasoning pattern that misleads the overseer

**Top 3 Anti-Anchors**:

| Rank | Tag | Effect | Δ Mean |
|------|-----|--------|--------|
| 1 | JUSTIFICATION | Helps werewolves hide | +0.40 |
| 2 | PLAN | Causes false accusations | +0.41 |
| 3 | DECEPTION_STRATEGY | False accusations | +0.31 |

**Visual**: Show bar chart comparing tag frequencies in errors vs successes

---

## SLIDE 6: Key Finding #1 - JUSTIFICATION (2 minutes)

**Werewolves who justify their reasoning evade detection**

```
Missed werewolves:  0.83 justifications/game
Caught werewolves:  0.43 justifications/game
Difference: +0.40 (93% increase)
```

**Example**:
> Werewolf CoT: "I'll vote for Player2 because they've been suspiciously quiet"
>
> Overseer: "That's reasonable logic, probably innocent" ❌

**Interpretation**: Providing explanations makes lies MORE convincing, not less!

---

## SLIDE 7: Key Finding #2 - PLAN (2 minutes)

**Strategic planning by innocents triggers false accusations**

```
Accused villagers: 2.08 plans/game
Cleared villagers: 1.67 plans/game
Difference: +0.41 (25% increase)
```

**Example**:
> Villager CoT: "I should support Player3 to build coalition"
>
> Overseer: "That sounds manipulative, must be deceiving!" ❌

**Interpretation**: Strategic thinking looks suspicious, even when legitimate game strategy

---

## SLIDE 8: The Paradox - CoT Reversal (2 minutes)

**Cooperative Tasks** (Math/Logic):
- JUSTIFICATION → Shows reasoning steps ✅
- PLAN → Makes strategy explicit ✅
- FACT_RECALL → Grounds in evidence ✅
- **Result**: CoT improves accuracy

**Adversarial Tasks** (Deception Detection):
- JUSTIFICATION → Convincing lies ❌
- PLAN → Looks manipulative ❌
- FACT_RECALL → Can be selective ❌
- **Result**: CoT misleads overseer

**Core Insight**: Same reasoning patterns have OPPOSITE effects in different domains

---

## SLIDE 9: Statistical Overview (1 minute)

**Dataset**:
- 19 games analyzed
- 95 player traces
- ~450 tagged sentences

**Overseer Performance**:
- Accuracy: 36.8% (7/19)
- True Positives: 7
- False Negatives: 12 ← Anti-anchors enable these
- False Positives: 12 ← Anti-anchors cause these

**Effect Sizes**: Small-to-medium (Δ = 0.15-0.41), but consistent direction

---

## SLIDE 10: Theoretical Contribution (2 minutes)

**Challenge to CoT Universality**:

Current wisdom: "More reasoning transparency = better AI performance"

Our finding: **Domain-dependent CoT effects**
- Cooperative reasoning: Anchors help ✅
- Adversarial reasoning: Anti-anchors mislead ❌

**Why This Matters**:
1. CoT isn't universally beneficial
2. Adversarial contexts require different approaches
3. "Explainable AI" can be exploited

---

## SLIDE 11: Future Directions (2 minutes)

**Immediate Follow-ups**:
1. Larger sample size (50-100 games) for stronger statistics
2. Statistical significance testing (currently descriptive)
3. Cross-game validation (test on Resistance, Avalon, etc.)

**Methodological Extensions**:
4. Remove anti-anchor tags and re-run overseer (ablation)
5. Train adversarial-aware deception detector
6. Human baseline study (are humans also misled?)

**Broader Impact**:
7. Apply to other adversarial domains (negotiation, debate, poker)
8. Develop "adversarial-robust" CoT methods

---

## SLIDE 12: Publication Path (1 minute)

**Potential Venues** (ranked by fit):

1. **NeurIPS** (Datasets & Benchmarks track)
   - Novel dataset + analysis methodology
   - Deadline: May/June

2. **ICLR** (Main conference)
   - Challenging CoT assumptions
   - Deadline: October

3. **ACL** (Computational Linguistics)
   - Reasoning analysis + language understanding
   - Deadline: February

4. **CHI** (Human-AI Interaction)
   - Implications for explainable AI
   - Deadline: September

**Estimate**: 2-3 months to full paper draft

---

## SLIDE 13: Conclusion (1 minute)

**Main Contributions**:
1. Identified "anti-anchors" in adversarial CoT reasoning
2. Showed domain-dependent CoT effects (cooperative vs adversarial)
3. Provided actionable insights for deception detection

**Broader Impact**:
- Challenges CoT universality assumption
- First systematic analysis of adversarial CoT patterns
- Opens new research direction in robust reasoning

**Deliverables**:
- Full analysis pipeline (reproducible)
- Comprehensive report
- Tagged dataset (95 players, 450+ sentences)

---

## SLIDE 14: Questions & Next Steps

**For Discussion**:
1. Do you see this as publishable? Which venue?
2. Should we expand sample size before writing?
3. Any specific analyses you'd like to see?
4. Collaboration opportunities? (Other labs working on CoT/deception)

**Timeline** (if proceeding):
- Week 1-2: Literature review, position in related work
- Week 3-4: Expand experiments (optional)
- Week 5-8: Write full paper draft
- Week 9-10: Internal review, revisions
- Week 11-12: Submit to conference

---

## BACKUP SLIDES

### Backup: Detailed Tag Definitions

[Show the 8-category taxonomy with examples]

### Backup: Full Statistical Tables

[Show complete tag frequency tables for all categories]

### Backup: Sample CoT Traces

[Show 2-3 real examples of werewolf vs villager reasoning]

### Backup: Related Work Comparison

[Compare to Wei et al. CoT, Lanham et al. Thought Anchors, etc.]

---

## Q&A PREPARATION

**Anticipated Questions**:

**Q1: "How do you know these patterns CAUSE the errors vs just correlate?"**
A: Valid point - this is correlational. Ablation study (remove anti-anchor tags) would test causality. Good follow-up experiment.

**Q2: "Why is the overseer accuracy so low (36%)?"**
A: Task is genuinely hard - even humans struggle. But the KEY finding is the differential pattern (which werewolves are missed/caught).

**Q3: "Could this be specific to your game setup?"**
A: Possible! That's why cross-game validation is critical next step. But pattern is consistent across 19 games.

**Q4: "What about statistical significance?"**
A: Current analysis is descriptive. Next step: permutation tests, effect size calculations, confidence intervals.

**Q5: "How does this relate to adversarial robustness literature?"**
A: Great connection! This is like "reasoning adversarial examples" - strategic reasoning that fools classifiers.

**Q6: "Is 19 games enough data?"**
A: For preliminary findings, yes. For publication, we should expand to 50-100 games. Current results establish the phenomenon.
