# Attribution Analysis: Critical CoT Components for Deception Detection

## Summary

This analysis identifies which components of Chain-of-Thought reasoning are most critical for detecting werewolves.

---

## 1. Sentence-Level Attribution

**Question**: Which Thought Anchor categories correlate with werewolf status?

| Category | Correlation | Werewolf % | Villager % |
|----------|-------------|------------|------------|
| JUSTIFICATION | 0.171 | 12.3% | 7.0% |
| ASSERTION | -0.316 | 27.2% | 42.4% |
| PLAN | -0.375 | 26.3% | 42.1% |
| OBSERVATION | nan | 0.0% | 0.0% |
| QUESTION | nan | 0.0% | 0.0% |
| EMOTIONAL | nan | 0.0% | 0.0% |
| META | nan | 0.0% | 0.0% |
| OTHER | nan | 0.0% | 0.0% |

**Interpretation**:
- Most werewolf-correlated: **JUSTIFICATION** (r=0.171)
- Most villager-correlated: **OTHER** (r=nan)

---

## 2. Deception Embedding Similarity

**Question**: Do werewolf CoTs have higher semantic similarity to deception concepts?

| Role | Mean Similarity to Deception |
|------|------------------------------|
| Werewolves | 0.6264 |
| Villagers | 0.6152 |
| **Difference** | **0.0112** |

**Interpretation**:
- Werewolf CoTs are 0.0112 more similar to deception concepts
- This suggests deceptive intent is semantically encoded in CoT

---

## Files Generated

- `sentence_attribution.csv` - Sentence type correlations
- `sentence_attribution.png` - Visualization
- `deception_similarity.csv` - Embedding similarities
- `deception_similarity_dist.png` - Distribution plot
- `token_importance.csv` - Word-level importance scores
- `ATTRIBUTION_REPORT.md` - This report

---

**Generated**: 2025-12-04 18:44:37.348627
**Embedding Model**: BAAI/bge-large-en-v1.5
