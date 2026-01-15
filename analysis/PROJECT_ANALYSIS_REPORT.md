# Comprehensive Project Analysis & Research Discoveries

## 1. Project Overview
**Project**: AI-Powered Werewolf Game
**Goal**: A Python implementation of the social deduction game Werewolf (Mafia) where AI agents (LLMs) play as players and an AI "Overseer" manages the game.
**Core Features**:
- **AI Players**: Agents with distinct personalities and strategies.
- **AI Overseer**: Manages game flow and fairness.
- **Research Focus**: Evaluating Chain-of-Thought (CoT) reasoning in adversarial contexts.

## 2. System Architecture
The project is structured into modular components:
- **Core Engine (`src/core/`)**:
  - `agents.py`: Implements `Werewolf`, `Villager`, `FortuneTeller` agents.
  - `engine.py`: Manages game execution, phases (Day/Night), and voting.
  - `prompts.py` & `llm.py`: Handles LLM interactions.
- **Filtering System (`src/filters/`)**:
  - `cot_filter.py`: **Critical Component**. Processes raw "inner thoughts" of agents into summaries for the Overseer.
  - `semantic_similarity_wrapper.py`: A new wrapper to improve filter quality using embeddings.
- **Analysis Tools (`analysis/`)**:
  - Scripts for statistical testing (H1-H4 hypotheses).
  - Experiments for CoT length and truncation.

## 3. The Research Narrative (The "H4" Discovery)

### The Original Hypotheses (H1-H3)
The research initially investigated if **Chain-of-Thought (CoT) length** negatively impacts deception detection.
- **H1**: Longer CoT \u2192 Lower accuracy. (Initially supported: p=0.015)
- **Hypothesis**: Information overload or innocent players appearing "strategic" due to verbosity causes errors.

### The "Accidental" Discovery (H4)
While testing a truncation hypothesis (H4: "Does shortening CoT help?"), a fundamental flaw was revealed.
- **Experiment**: Comparison of the original Overseer vs. a new "H4 Overseer" with truncated CoT.
- **Result**:
  - **Original Overseer**: 36.8% accuracy (Filtering enabled).
  - **H4 Overseer**: **100% accuracy** (Direct raw CoT access).
- **Control**: Accuracy remained 100% even when CoT was truncated to 25%.

### Conclusion
**The problem was never the length of the CoT. The problem was the Filter.**
The `AdvancedCoTFilter` was destroying the signal required to detect deception.

## 4. Technical Root Cause Analysis

### The Flawed Component: `AdvancedCoTFilter`
**File**: `src/filters/cot_filter.py`
**Mechanism**:
1.  **Keyword Counting**: Counts words like "deflect", "strategy", "plan".
2.  **Heuristic Rules**: "If > 5 sentences and contains 'because', label as 'excessive justification'."
3.  **Output**: Generates a summary like:
    > "- HIGH deception indicators (5 signals)"
    > "- Deceptive language: deception: 'deflect', deception: 'target'"

**Why It Failed**:
- **False Equivalence**: Both liars and truthful players use similar vocabulary (e.g., "I need to *deflect* suspicion" vs "I hope they don't *deflect* to me").
- **Context Destruction**: The filter strips away the *semantic meaning* and *intent*, leaving only behavioral flags.
- **Length Confound**: Longer CoT naturally contains more keywords, leading the filter to flag *everyone* with long CoT as suspicious. This created the spurious correlation observed in H1.

### The Fix: `SemanticSimilarityWrapper`
**File**: `src/filters/semantic_similarity_wrapper.py`
**Mechanism**:
- Uses **Embeddings** (`bge-large-en-v1.5`) to measure semantic similarity between Raw CoT and the Filtered Summary.
- Uses an LLM (Claude) to iteratively rewrite the summary until similarity \u2265 0.80.
- **Goal**: Preserve the *meaning* (deceptive intent) while still providing a summary.

## 5. Strategic Recommendations

### Immediate Action: Pivot Publication Focus
The original premise ("Length hurts performance") is an artifact. The **real** discovery is much more significant:
> **"Information Loss in CoT Filtering Destroys Adversarial Detection"**

**Why this is a stronger paper:**
1.  **Effect Size**: +63.2% accuracy improvement (Huge).
2.  **Causality**: Proven via A/B test on identical games.
3.  **Relevance**: Critical for AI Safety and Oversight (monitoring systems often use summarization).

### Next Steps (per docs)
1.  **Discard H1-H3**: These were based on the flawed filter metrics.
2.  **Focus on the H4 Result**: Writing up the "Filter vs No-Filter" comparison.
3.  **Validation**:
    - Run ~50 more games to confirm the 100% accuracy robustness.
    - Analyze exactly *what* information is lost (Semantic Analysis).

## 6. Summary of Key Files
- **`docs/research_summaries/DISCOVERY_SUMMARY.md`**: Executive summary of the 100% accuracy finding.
- **`docs/research_summaries/H4_CRITICAL_DISCOVERY.md`**: Detailed technical breakdown.
- **`src/filters/cot_filter.py`**: The "broken" keyword-based filter.
- **`analysis/experiment1_h4_truncation_causal.py`**: The script that revealed the truth.
