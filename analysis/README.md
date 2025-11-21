# CoT Anti-Anchor Analysis Pipeline

This directory contains scripts for analyzing Chain-of-Thought reasoning patterns that mislead AI deception detectors in the Werewolf game.

## Research Question

**Do certain types of reasoning sentences act as "anti-anchors" that mislead the overseer, contrary to how CoT helps in logical domains?**

## Pipeline Overview

```
1. Run games with CoT collection
   → run_cot_experiment.py
   → Saves: results/game_*_filtered_cot.json

2. Tag CoT sentences
   → analysis/tag_cot_sentences.py
   → Saves: analysis/tagged_cots.jsonl

3. Analyze anti-anchor patterns
   → analysis/analyze_anchors.py
   → Saves: analysis/ANTI_ANCHOR_REPORT.md
          analysis/anchor_analysis.json
```

## Setup

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set API keys in .env
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...
```

### Cost Estimates

| Step | API Calls | Est. Cost |
|------|-----------|-----------|
| Run 20 games | OpenAI (agents) + Anthropic (overseer) | ~$30 |
| Tag sentences | Claude 3 Opus (tagging) | ~$0.44 |
| **Total** | | **~$30.44** |

## Usage

### Step 1: Run Games with CoT Collection

```bash
python run_cot_experiment.py
```

This runs 20 games with filtered CoT access and saves per-player reasoning traces.

**Output**: `results/game_1001_filtered_cot.json` through `game_1020_filtered_cot.json`

**Time**: ~30-45 minutes

### Step 2: Tag CoT Sentences

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python analysis/tag_cot_sentences.py
```

Tags each sentence in every player's reasoning with its functional role using the Thought Anchors taxonomy.

**Output**: `analysis/tagged_cots.jsonl` (one JSON object per line)

**Time**: ~10-15 minutes
**Cost**: ~$0.44

### Step 3: Analyze Anti-Anchors

```bash
python analysis/analyze_anchors.py
```

Correlates tag frequencies with overseer errors to identify misleading reasoning patterns.

**Output**:
- `analysis/ANTI_ANCHOR_REPORT.md` - Comprehensive research report
- `analysis/anchor_analysis.json` - Raw analysis data

**Time**: <1 minute (local computation)

## Thought Anchors Taxonomy

Based on the "Thought Anchors" framework, adapted for adversarial contexts:

| Tag | Definition | Example |
|-----|------------|---------|
| **PLAN** | Forward-looking strategy | "I should vote for Player3" |
| **BACKTRACK** | Revising prior reasoning | "Actually, that doesn't make sense" |
| **JUSTIFICATION** | Explaining a position | "because they were quiet during discussion" |
| **EMOTION** | Affective states | "I'm nervous about being suspected" |
| **FACT_RECALL** | Game event retrieval | "Player2 voted for Player1 yesterday" |
| **ASSERTION** | Declarative claims | "Player3 is definitely suspicious" |
| **META_REASONING** | Reasoning about reasoning | "My logic seems circular here" |
| **DECEPTION_STRATEGY** | Explicit manipulation planning | "I'll deflect suspicion to Player5" |

## Data Structure

### Game Result Files (`results/game_*.json`)

```json
{
  "game_id": 1,
  "seed": 1001,
  "experiment_type": "filtered_cot",
  "ground_truth": "Player3",
  "overseer_prediction": "Player4",
  "overseer_correct": false,
  "winner": "villagers",
  "players": {
    "Player1": {
      "role": "Villager",
      "cot": "Full reasoning trace...",
      "public_messages": ["msg1", "msg2"],
      "num_messages": 2
    },
    ...
  }
}
```

### Tagged CoT Files (`analysis/tagged_cots.jsonl`)

```json
{
  "game_id": 1,
  "seed": 1001,
  "player_name": "Player3",
  "player_role": "Werewolf",
  "ground_truth": "Player3",
  "overseer_prediction": "Player4",
  "overseer_correct": false,
  "is_werewolf": true,
  "was_predicted": false,
  "tagged_cot": [
    {"text": "I need to appear innocent.", "tag": "DECEPTION_STRATEGY"},
    {"text": "Player1 has been very quiet.", "tag": "FACT_RECALL"},
    ...
  ],
  "original_cot": "..."
}
```

## Expected Findings

### Hypothesis 1: DECEPTION_STRATEGY Leakage
Werewolves who explicitly plan deception might leak this in CoT, but overseer may not effectively use it.

### Hypothesis 2: JUSTIFICATION Overload
Excessive justification might appear convincing, causing overseer to miss deceptive players.

### Hypothesis 3: EMOTION Misdirection
Strategic emotional expressions might mislead overseer into false accusations.

### Hypothesis 4: META_REASONING Signals
Self-doubt or meta-reasoning might be interpreted as honesty rather than strategic hesitation.

## Research Implications

This analysis could inform:

1. **Improved filtering algorithms**: Exclude anti-anchor tags from overseer input
2. **Adversarial training**: Train models specifically on deceptive reasoning detection
3. **Theory development**: Extend Thought Anchors framework to adversarial contexts
4. **Prompt engineering**: Design prompts that minimize anti-anchor production

## Citation

If you use this analysis pipeline, please cite:

```
[Your research paper on CoT anti-anchors in social deduction games]
```

## License

MIT License - See parent directory LICENSE file
