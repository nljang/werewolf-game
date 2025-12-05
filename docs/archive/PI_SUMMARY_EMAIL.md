# Email to PI: Anti-Anchor Research Summary

**Subject**: Follow-up Analysis: Why CoT Fails in Deception Detection

---

Hi [PI Name],

Following up on our Werewolf CoT experiment (which showed CoT didn't improve overseer accuracy), I ran a deeper analysis to understand **why** CoT fails in adversarial contexts. The findings are quite interesting and may be publishable.

## Quick Summary

**Research Question**: Which types of reasoning sentences in CoT mislead the AI overseer?

**Method**:
- Ran 19 games collecting full reasoning traces
- Tagged 95 player CoT logs using Thought Anchors taxonomy (8 sentence types)
- Correlated tag frequencies with overseer errors

**Key Finding**: Identified "anti-anchors" - reasoning patterns that mislead the overseer (opposite of helpful anchors in math/logic)

## Top 3 Anti-Anchors

1. **JUSTIFICATION** helps werewolves evade detection
   - Missed werewolves used 0.83 justifications vs 0.43 for caught werewolves
   - Providing explanations makes deception MORE convincing

2. **PLAN** causes false accusations of innocents
   - Wrongly accused villagers used 2.08 planning statements vs 1.67 for cleared
   - Strategic thinking looks suspicious even when innocent

3. **DECEPTION_STRATEGY** backfires on innocent players
   - Accused villagers used 0.42 vs 0.11 for cleared
   - Meta-strategic reasoning triggers false alarms

## Why This Matters

**Domain-Specific CoT Behavior**: This challenges the assumption that CoT universally improves AI reasoning. In adversarial contexts:
- Math/Logic: Reasoning shows path to truth → helpful ✅
- Deception: Reasoning can be strategic lies → misleading ❌

## Next Steps

I've prepared:
- Full research report (analysis/ANTI_ANCHOR_REPORT.md)
- Raw data and analysis scripts (all reproducible)
- Draft paper structure (if you think this is publishable)

**Potential venues**: NeurIPS (Datasets & Benchmarks), ICLR, ACL (Computational Linguistics), or CHI (Human-AI Interaction)

Would you like to meet to discuss this further? I can present the detailed findings and we can decide if it's worth developing into a full paper.

Best,
[Your Name]

---

**Attachments**:
- analysis/ANTI_ANCHOR_REPORT.md (full report)
- PI_PRESENTATION_SLIDES.pdf (if presenting in person)
