# Experiment 1 - H4: Truncation Results

## Hypothesis
**H4**: Truncating CoT traces improves overseer accuracy in deception detection

**Prediction**: Accuracy should INCREASE as CoT length DECREASES

## Results Summary

### Accuracy by Truncation Level

| CoT Kept (%)   | Accuracy   | Correct   |
|:---------------|:-----------|:----------|
| 25%            | 100.0%     | 19/19     |
| 50%            | 100.0%     | 19/19     |
| 75%            | 100.0%     | 19/19     |
| 100%           | 100.0%     | 19/19     |


### Effect Size (100% vs 25%)

- **Accuracy at 100%**: 100.0%
- **Accuracy at 25%**: 100.0%
- **Difference**: +0.0%
- **Cohen's h**: 0.000 (small (<0.2))

### Paired Comparison: 100% vs 25% (McNemar Test)

**Contingency Table**:
- Both correct: 19
- Only 100% correct: 0
- Only 25% correct: 0
- Both wrong: 0

**Test Result**:
- χ² = 0.000, p = 1.000
- **Interpretation**: No difference
- **Conclusion**: ❌ NOT SIGNIFICANT

### Trend Analysis

**Linear Correlation** (truncation level vs correctness):
- Pearson r = nan, p = nan
- Positive = more CoT helps
- **Conclusion**: ❌ **H4 NOT SUPPORTED**


## Interpretation

See figures:
- `h4_truncation_main_result.png` - Main accuracy plot
- `h4_truncation_trajectories.png` - Per-game trajectories
