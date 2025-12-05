# Experiment Status

## Pipeline Progress

### ✅ Setup Complete
- [x] Analysis directory created
- [x] Experiment scripts created
- [x] API keys configured
- [x] Dependencies installed

### 🔄 Step 1: Running 20 CoT Games (IN PROGRESS)
**Status**: Running in background (PID check with `ps aux | grep run_cot_experiment`)

**Progress**: Check with `./check_progress.sh` or `ls results/ | wc -l`

**Expected**:
- Duration: 30-45 minutes
- Output: 20 × `results/game_XXXX_filtered_cot.json`
- Cost: ~$30

### ⏳ Step 2: Tag CoT Sentences (PENDING)
**Command**: `python analysis/tag_cot_sentences.py`

**Requirements**:
- All 20 games completed
- ANTHROPIC_API_KEY in environment

**Expected**:
- Duration: 10-15 minutes
- Output: `analysis/tagged_cots.jsonl`
- Cost: ~$0.44

### ⏳ Step 3: Analyze Anti-Anchors (PENDING)
**Command**: `python analysis/analyze_anchors.py`

**Requirements**:
- Tagged CoT data from Step 2

**Expected**:
- Duration: <1 minute
- Output: `analysis/ANTI_ANCHOR_REPORT.md`, `analysis/anchor_analysis.json`
- Cost: $0 (local computation)

## Quick Commands

```bash
# Check progress
./check_progress.sh

# View experiment log
tail -f experiment_output.log

# Count completed games
ls -1 results/*.json | wc -l

# Stop experiment (if needed)
pkill -f run_cot_experiment.py

# Resume monitoring
ps aux | grep run_cot_experiment
```

## Troubleshooting

### If experiment stalls:
1. Check process: `ps aux | grep run_cot_experiment`
2. Check last game: `ls -lt results/ | head -5`
3. Check errors: `tail -50 experiment_output.log`

### If API rate limited:
- Wait a few minutes
- Experiment has 1s delay between games

### If out of credits:
- Check OpenAI dashboard: https://platform.openai.com/usage
- Check Anthropic console: https://console.anthropic.com/settings/billing

## Next Steps After Completion

Once all 20 games finish:

```bash
# Step 2: Tag sentences
export ANTHROPIC_API_KEY=sk-ant-...
python analysis/tag_cot_sentences.py

# Step 3: Analyze
python analysis/analyze_anchors.py

# Step 4: Review
cat analysis/ANTI_ANCHOR_REPORT.md
```
