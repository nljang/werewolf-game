# Werewolf Game: Project Structure

## Directory Organization

```
werewolf-game/
├── README.md                    # Main project readme
├── PROJECT_STRUCTURE.md         # This file
├── requirements.txt             # Python dependencies
│
├── src/                         # Source code
│   ├── core/                    # Core game engine
│   │   ├── agents.py           # Player agents (Werewolf, Villager, FortuneTeller)
│   │   ├── engine.py           # Game engine logic
│   │   ├── llm.py              # LLM provider interface
│   │   ├── schemas.py          # Data schemas (Pydantic models)
│   │   ├── prompts.py          # Prompt templates
│   │   ├── config.py           # Configuration
│   │   ├── logging_utils.py    # Logging utilities
│   │   └── main.py             # Main entry point
│   │
│   ├── filters/                 # CoT filtering systems
│   │   ├── cot_filter.py       # AdvancedCoTFilter (keyword-based, BROKEN)
│   │   └── semantic_similarity_wrapper.py  # Semantic-preserving wrapper
│   │
│   └── experiments/             # Experiment runners
│       ├── experiment.py       # Base experiment class
│       └── run_cot_experiment.py  # CoT experiment runner
│
├── analysis/                    # Analysis scripts and outputs
│   ├── tag_cot_sentences.py    # Thought Anchors tagging
│   ├── analyze_anchors.py      # Anti-anchor analysis
│   ├── experiment1_length_analysis.py  # H1-H3 statistical tests
│   ├── experiment1_h4_truncation_causal.py  # H4 truncation experiment
│   ├── embedding_similarity_analysis.py  # Embedding similarity study
│   │
│   ├── tagged_cots.jsonl       # Tagged sentence data
│   │
│   └── experiment1_output/     # All Experiment 1 results
│       ├── EXPERIMENT1_H1_H2_H3_REPORT.md
│       ├── EXPERIMENT1_H4_REPORT.md
│       ├── EMBEDDING_SIMILARITY_REPORT.md
│       ├── h1_h2_length_accuracy.png
│       ├── h3_mediation_scatter.png
│       ├── h4_truncation_main_result.png
│       ├── h4_truncation_trajectories.png
│       ├── embedding_similarity_overview.png
│       ├── embedding_tsne_comparison.png
│       ├── embedding_information_loss_trajectories.png
│       ├── analysis_dataframe.csv
│       ├── h4_truncation_results.csv
│       └── embedding_similarity_analysis.csv
│
├── results/                     # Game results data
│   └── game_*_filtered_cot.json  # Individual game results with CoT
│
├── logs/                        # Execution logs
│   ├── h4_experiment_log.txt
│   └── game_log.json
│
└── docs/                        # Documentation
    ├── research_summaries/      # Key findings
    │   ├── DISCOVERY_SUMMARY.md       # H4 filter discovery (MAIN RESULT)
    │   ├── H4_CRITICAL_DISCOVERY.md   # Detailed technical analysis
    │   └── EXPERIMENT1_SUMMARY_FOR_PI.md  # Complete H1-H4 summary
    │
    ├── guides/                  # How-to guides
    │   ├── QUICKSTART.md
    │   └── RUN_H4_GUIDE.md
    │
    └── archive/                 # Old/redundant documents
        ├── EMAIL_TO_PI.md
        ├── PI_SUMMARY_EMAIL.md
        ├── H4_ONE_PAGE_SUMMARY.md
        └── ...
```

---

## Key Files Reference

### 📊 Main Research Findings

| File | Description |
|------|-------------|
| **docs/research_summaries/DISCOVERY_SUMMARY.md** | **H4 Discovery: Filter destroyed deception detection** |
| docs/research_summaries/H4_CRITICAL_DISCOVERY.md | Full technical analysis of filter problem |
| docs/research_summaries/EXPERIMENT1_SUMMARY_FOR_PI.md | Complete H1-H4 results for PI meeting |

### 🔧 Core System

| File | Description |
|------|-------------|
| src/core/agents.py | Player agents with AdvancedFilterOverseer |
| src/filters/cot_filter.py | **AdvancedCoTFilter (the broken filter)** |
| src/filters/semantic_similarity_wrapper.py | **New: Semantic-preserving filter wrapper** |

### 🧪 Experiments

| File | Description |
|------|-------------|
| analysis/experiment1_h4_truncation_causal.py | **H4 experiment (revealed filter problem)** |
| analysis/embedding_similarity_analysis.py | **Embedding study (0.68 similarity)** |
| analysis/experiment1_length_analysis.py | H1-H3 correlation analysis |

### 📈 Results

| File | Description |
|------|-------------|
| analysis/experiment1_output/EMBEDDING_SIMILARITY_REPORT.md | Embedding analysis results |
| analysis/experiment1_output/EXPERIMENT1_H4_REPORT.md | H4 statistical report |
| analysis/experiment1_output/h4_truncation_results.csv | H4 raw data (76 predictions) |

---

## Quick Navigation

### To run the game:
```bash
python -m src.core.main
```

### To run H4 experiment:
```bash
python analysis/experiment1_h4_truncation_causal.py
```

### To run embedding analysis:
```bash
python analysis/embedding_similarity_analysis.py
```

### To test semantic wrapper:
```bash
python -m src.filters.semantic_similarity_wrapper
```

---

## Research Timeline

1. **Initial Experiment** → CoT didn't help (15% vs 10.5%)
2. **H1-H3 Analysis** → Found "length hurts" correlation
3. **H4 Experiment** → Discovered filter was the actual problem
4. **Embedding Study** → Confirmed filter loses 32% semantic information
5. **Semantic Wrapper** → New filter that preserves semantics

---

## The Discovery

**Problem**: AdvancedCoTFilter reduces CoT to keyword summaries
- "I need to deflect suspicion" → "HIGH deception indicators"
- Everyone looks the same after filtering

**Evidence**:
- Original overseer (with filter): 36.8% accuracy
- H4 overseer (no filter): 100% accuracy
- Embedding similarity: 0.68 (moderate preservation)

**Solution**: SemanticSimilarityWrapper maintains similarity ≥ 0.80

---

**Last Updated**: 2025-11-27
