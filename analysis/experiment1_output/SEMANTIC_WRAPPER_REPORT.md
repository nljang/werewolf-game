# Semantic Similarity Wrapper: Full Results

## Summary

Applied SemanticSimilarityWrapper to all 95 player traces from 19 games.

**Goal**: Improve filtered summaries to maintain semantic similarity ≥ 0.80 with raw CoT.

---

## Overall Results

| Metric | Value |
|--------|-------|
| **Total traces processed** | 95 |
| **Original mean similarity** | 0.6902 |
| **Improved mean similarity** | 0.7932 |
| **Mean improvement** | +0.1030 |
| **Success rate** (≥0.80) | 47.4% (45/95) |
| **Mean attempts used** | 2.11 |

**Interpretation**:
- Original AdvancedCoTFilter: 0.69 similarity (moderate preservation)
- Improved wrapper: 0.79 similarity (+0.10 improvement)
- Success rate: 47% of traces reached ≥0.80 threshold

---

## By Role

### Werewolves (n=19)

| Metric | Value |
|--------|-------|
| **Original similarity** | 0.6752 |
| **Improved similarity** | 0.7876 |
| **Mean improvement** | +0.1124 |
| **Success rate** | 42.1% |

### Villagers (n=76)

| Metric | Value |
|--------|-------|
| **Original similarity** | 0.6939 |
| **Improved similarity** | 0.7946 |
| **Mean improvement** | +0.1006 |
| **Success rate** | 48.7% |

---

## Distribution Statistics

### Original Similarity
- Min: 0.5513
- 25th percentile: 0.6730
- Median: 0.6965
- 75th percentile: 0.7157
- Max: 0.7647

### Improved Similarity
- Min: 0.6978
- 25th percentile: 0.7730
- Median: 0.7960
- 75th percentile: 0.8166
- Max: 0.8403

---

## Attempt Distribution

| Attempts | Count | Percentage |
|----------|-------|------------|
| 0 (already ≥0.80) | 0 | 0.0% |
| 1 | 41 | 43.2% |
| 2 | 3 | 3.2% |
| 3 (max) | 51 | 53.7% |

---

## Key Findings

1. **Improvement achieved**: Mean similarity increased from 0.69 → 0.79 (+0.10)

2. **Success rate**: 47% of traces reached ≥0.80 threshold

3. **Role differences**:
   - Werewolves: +0.112 improvement
   - Villagers: +0.101 improvement

4. **Efficiency**: Average 2.1 attempts per trace

---

## Comparison to Original H4 Finding

**Original discovery**:
- AdvancedCoTFilter (no wrapper): 0.68 similarity, 37% overseer accuracy
- Direct CoT (no filter): 1.00 similarity, 100% overseer accuracy

**With SemanticSimilarityWrapper**:
- Filtered + Wrapper: 0.79 similarity
- **Prediction**: Should achieve ~61% overseer accuracy (between 37% and 100%)

---

## Files Generated

1. **semantic_filter_output.csv** - Summary statistics
2. **semantic_filter_output.jsonl** - Full results with text
3. **semantic_wrapper_results.png** - Distribution plots
4. **SEMANTIC_WRAPPER_REPORT.md** - This report

---

**Generated**: 2025-12-02 17:22:23
**Model**: BAAI/bge-large-en-v1.5 (embeddings), Claude Sonnet (summary improvement)
**Sample**: 95 player traces from 19 games
