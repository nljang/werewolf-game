# H4 Truncation Experiment: Execution Guide

## What H4 Tests (The Critical Question)

**H1-H3 showed correlation**: "Longer CoT is associated with worse accuracy"

**H4 tests causation**: "Artificially shortening CoT improves accuracy"

This is the **causal/interventional** test that makes the paper strong.

---

## How It Works

### Design
1. Take each of the 19 games
2. Create 4 variants with truncated CoT: 25%, 50%, 75%, 100%
   - Keep **first N%** of sentences (preserves temporal coherence)
3. Re-run overseer prediction on each variant
4. Compare accuracy across truncation levels

### Total Work
- **76 overseer calls** (19 games × 4 levels)
- **~$38 cost** ($0.50 per Claude Opus call)
- **~30-40 minutes** runtime (2-3 sec per call)

---

## Running the Experiment

### Option 1: Real API (Recommended for Paper)

```bash
# Set API key
export ANTHROPIC_API_KEY=sk-ant-api03-...

# Run experiment
python analysis/experiment1_h4_truncation_causal.py
```

**What happens**:
1. Loads 19 game files from `results/`
2. Shows cost/time estimate
3. Asks for confirmation
4. Runs 76 overseer predictions
5. Saves results + analysis + plots

**Outputs**:
- `analysis/experiment1_output/h4_truncation_results.csv` - Raw data
- `analysis/experiment1_output/EXPERIMENT1_H4_REPORT.md` - Statistical report
- `analysis/experiment1_output/h4_truncation_main_result.png` - Main figure
- `analysis/experiment1_output/h4_truncation_trajectories.png` - Per-game plots

---

### Option 2: Placeholder Mode (Testing Only)

```bash
# No API key set
python analysis/experiment1_h4_truncation_causal.py
```

**What happens**:
1. Warns that no API key is set
2. Asks if you want to continue with random guesses
3. Runs quickly with placeholder results
4. Useful for testing the pipeline, NOT for real results

---

## Expected Results

### If H4 is SUPPORTED (Strong Paper):

```
Accuracy by truncation level:
  25%: 55% ← Much better!
  50%: 48%
  75%: 42%
 100%: 37% ← Current (from H1-H3)

Trend: r = -0.XX, p < 0.05
✅ H4 STRONGLY SUPPORTED
```

**Interpretation**: "Removing 75% of CoT improves accuracy by 18 percentage points (37%→55%, p<0.05). This provides causal evidence that CoT length hurts deception detection."

---

### If H4 is WEAK (Still Publishable):

```
Accuracy by truncation level:
  25%: 42%
  50%: 40%
  75%: 38%
 100%: 37%

Trend: r = -0.XX, p = 0.12
⚠️ H4 WEAKLY SUPPORTED
```

**Interpretation**: "Trend in predicted direction but not statistically significant. May need larger sample."

---

### If H4 FAILS (Need to Rethink):

```
Accuracy by truncation level:
  25%: 35%
  50%: 36%
  75%: 37%
 100%: 37%

Trend: r = +0.XX, p = 0.65
❌ H4 NOT SUPPORTED
```

**Interpretation**: "No improvement from truncation. H1's length effect may be spurious or confounded."

---

## Statistical Tests Performed

### 1. McNemar Test (100% vs 25%)
**Paired comparison** on same games:
- Counts: How many games flip from wrong→correct or correct→wrong
- More sensitive than independent proportions test
- Reports: χ², p-value, interpretation

### 2. Trend Test (Pearson Correlation)
**Linear relationship** between truncation and accuracy:
- Tests if accuracy monotonically improves as CoT decreases
- Reports: r, p-value
- Strong evidence if r < 0 and p < 0.05

### 3. Effect Size (Cohen's h)
**Magnitude of effect**:
- Small: h < 0.2
- Medium: 0.2 < h < 0.5
- Large: h > 0.5

---

## What to Check After Running

### 1. Look at the main plot
`h4_truncation_main_result.png`

**Good sign**: Downward-sloping line (left to right)
**Bad sign**: Flat or upward-sloping

### 2. Check the report
`EXPERIMENT1_H4_REPORT.md`

Look for:
- Trend test p-value < 0.05
- McNemar test p-value < 0.05
- Cohen's h > 0.2

### 3. Inspect trajectories
`h4_truncation_trajectories.png`

**Good sign**: Most gray lines slope downward
**Bad sign**: Lines are random/horizontal

---

## Troubleshooting

### "No game files found"
- Make sure you ran Step 1 (20 games experiment)
- Game files should be in `results/game_*_filtered_cot.json`

### "API rate limit exceeded"
- Script already has 2-second delays
- If still hitting limits, increase `time.sleep(2)` to `time.sleep(5)`

### "Prediction extraction failed"
- Check `raw_response` field in results CSV
- May need to adjust `extract_prediction_from_response()` regex

### "Convergence warning"
- This is OK for descriptive stats
- Report the trend anyway

---

## After Results: Update Summary Documents

Once H4 completes, update:

1. **EXPERIMENT1_SUMMARY_FOR_PI.md**
   - Replace "⏳ READY TO TEST" with actual H4 results
   - Add H4 figure to the document

2. **EXPLAIN_EXPERIMENT1_SIMPLE.md**
   - Fill in actual H4 results instead of predictions

3. Create final presentation with all 4 hypotheses tested

---

## Timeline for Full Experiment 1

| Task | Time | Cost | Status |
|------|------|------|--------|
| H1-H3 Analysis | Done | $0 | ✅ Complete |
| H4 Execution | 30-40 min | $38 | ⏳ Ready to run |
| Update documents | 1 hour | $0 | After H4 |
| **Total** | **~2 hours** | **$38** | |

---

## Why This Matters

**H1-H3 without H4**: "Length correlates with errors" (interesting but weak)

**H1-H3 with H4**: "Length CAUSES errors" (strong causal claim)

The difference:
- Observational → Experimental
- Correlation → Causation
- "Associated with" → "Causes"

**This makes the paper much stronger for peer review.**

---

## Next Steps After H4

### If H4 succeeds:
1. Run with H4 results
2. Update all summary documents
3. Draft full paper
4. Submit to conference

### If H4 fails:
1. Investigate why (may need different truncation strategy)
2. Try alternative tests (e.g., truncate from end instead of start)
3. Expand sample size and re-test
4. May still publish H1-H3 as exploratory findings

---

**Ready to run?**

```bash
export ANTHROPIC_API_KEY=your-key-here
python analysis/experiment1_h4_truncation_causal.py
```
