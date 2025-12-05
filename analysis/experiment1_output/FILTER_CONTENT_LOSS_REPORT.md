# Filter Content Loss Analysis

## Summary

This analysis examines what information the old filter deleted and how the new filter preserves it differently.

---

## 1. Sentence Type Preservation

**Question**: Which types of sentences did the old filter delete?

| Category | Old Rate | New Rate | Improvement |
|----------|----------|----------|-------------|
| JUSTIFICATION | 19.7% | 100.0% | +80.3pp |
| ASSERTION | 20.2% | 92.0% | +71.7pp |
| PLAN | 19.7% | 88.6% | +68.8pp |

**Key Findings**:
- Worst preserved by old filter: **PLAN** (19.7%)
- Biggest improvement: **JUSTIFICATION** (+80.3pp)

---

## 2. Deception Cue Preservation

**Question**: Were specific deception-related words preserved?

| Cue | Old Rate | New Rate | Improvement |
|-----|----------|----------|-------------|
| werewolf | 0.0% | 100.0% | +100.0pp |
| trust | 0.0% | 83.7% | +83.7pp |
| villager | 0.0% | 66.7% | +66.7pp |
| lie | 0.0% | 10.0% | +10.0pp |
| defend | 0.0% | 0.0% | +0.0pp |
| deflect | 100.0% | 100.0% | +0.0pp |
| innocent | 0.0% | 0.0% | +0.0pp |
| lying | 0.0% | 0.0% | +0.0pp |
| manipulate | 0.0% | 0.0% | +0.0pp |
| suspect | 0.0% | 0.0% | +0.0pp |
| suspicious | 88.9% | 83.3% | +-5.6pp |

**Key Findings**:
- Most improved cue: **werewolf** (+100.0pp)
- Overall: Old filter preserved 17.2% of cues, new filter preserved 40.3%

---

## 3. Compression vs Semantic Preservation

| Filter | Compression | Similarity |
|--------|-------------|------------|
| Old | 65.3% | 0.6902 |
| New | 191.0% | 0.7932 |

**Trade-off**:
- New filter is 125.7pp more compressed
- New filter preserves 0.1030 more semantic information

---

## Files Generated

- `filter_sentence_preservation.csv` - Sentence type preservation rates
- `filter_preservation_comparison.png` - Visualization
- `deception_cue_preservation.csv` - Cue-level preservation
- `deception_cue_preservation.png` - Cue visualization
- `compression_vs_similarity.csv` - Compression analysis
- `compression_vs_similarity.png` - Scatter plot
- `FILTER_CONTENT_LOSS_REPORT.md` - This report

---

**Generated**: 2025-12-04 18:44:51.125748
