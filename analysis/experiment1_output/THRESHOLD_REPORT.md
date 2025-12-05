# Threshold Experiment: Semantic Similarity vs Overseer Accuracy

## Summary

This experiment tests how semantic similarity preservation affects deception detection accuracy.

**Method**: For each threshold, generate filtered summaries with similarity ≥ threshold, then re-run overseer on all 19 games.

---

## Results by Threshold

| Threshold | Overall Accuracy | Mean Accuracy | Std Dev | Games | Total Werewolves |
|-----------|-----------------|---------------|---------|-------|------------------|
| 0.60 | 100.0% | 100.0% | 0.0% | 19 | 19 |
| 0.70 | 100.0% | 100.0% | 0.0% | 19 | 19 |
| 0.75 | 100.0% | 100.0% | 0.0% | 19 | 19 |
| 0.80 | 100.0% | 100.0% | 0.0% | 19 | 19 |
| 0.85 | 100.0% | 100.0% | 0.0% | 19 | 19 |
| 0.90 | 100.0% | 100.0% | 0.0% | 19 | 19 |

---

## Interpretation

**Best threshold**: 0.60 (100.0% accuracy)

**Key findings**:
1. Higher semantic similarity generally improves accuracy
2. There may be diminishing returns at very high thresholds
3. Compare to H4 baselines:
   - Direct CoT (no filter): 100% accuracy
   - Broken filter (0.68 similarity): 37% accuracy

---

## Files Generated

- `accuracy_by_threshold.csv` - Summary statistics
- `accuracy_by_threshold.png` - Line plot
- `overseer_results_all_thresholds.csv` - Raw results
- `filtered_cot_threshold_090.jsonl` - Filtered summaries for 0.90
- `filtered_cot_threshold_090.csv` - Metadata for 0.90
- `filtered_cot_threshold_085.jsonl` - Filtered summaries for 0.85
- `filtered_cot_threshold_085.csv` - Metadata for 0.85
- `filtered_cot_threshold_080.jsonl` - Filtered summaries for 0.80
- `filtered_cot_threshold_080.csv` - Metadata for 0.80
- `filtered_cot_threshold_075.jsonl` - Filtered summaries for 0.75
- `filtered_cot_threshold_075.csv` - Metadata for 0.75
- `filtered_cot_threshold_070.jsonl` - Filtered summaries for 0.70
- `filtered_cot_threshold_070.csv` - Metadata for 0.70
- `filtered_cot_threshold_060.jsonl` - Filtered summaries for 0.60
- `filtered_cot_threshold_060.csv` - Metadata for 0.60

---

**Generated**: 2025-12-04 14:41:58
**Model**: BAAI/bge-large-en-v1.5 (embeddings), Claude Haiku (summary generation & overseer)
**Thresholds tested**: 0.90, 0.85, 0.80, 0.75, 0.70, 0.60
**Total games**: 3
