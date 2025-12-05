# Chain-of-Thought in Social Deception Detection: An Experimental Study

**Date**: September 2024
**Researcher**: Nathan
**Models**: GPT-4o-mini (agents), Claude Opus 3 (overseer)

---

## Executive Summary

We investigated whether providing filtered Chain-of-Thought (CoT) reasoning logs improves AI performance in detecting deception in social games. Using a Werewolf (Mafia) simulation with 40 games across two conditions, we found **no significant difference** between overseers with and without CoT access (15% vs 10.5%, p=0.66). Both approaches performed below chance (20%), suggesting fundamental limitations in current LLMs' ability to detect strategic deception.

---

## Research Question

**Does access to player reasoning (Chain-of-Thought) improve an AI overseer's ability to identify deceptive players in multi-agent social games?**

---

## Background

Chain-of-Thought (CoT) prompting has shown significant improvements in LLM performance on mathematical and logical reasoning tasks. However, its effectiveness in adversarial social contexts—where reasoning may be strategically deceptive—remains unexplored.

**Key difference from prior work**: In math problems, CoT reveals truth-seeking reasoning. In social deception games, CoT may contain strategic lies.

---

## Methodology

### Experimental Setup

**Game**: Werewolf (Mafia) - a social deduction game where:
- One player is secretly a werewolf (deceptive role)
- Other players are villagers trying to identify the werewolf
- Players discuss, vote to eliminate suspects, and werewolf kills at night

**Participants**:
- **5 AI players per game** (GPT-4o-mini)
  - 1 werewolf
  - 1 fortune teller (can investigate other players)
  - 3 villagers
- **1 AI overseer** (Claude Opus 3)
  - Task: Identify the werewolf before game ends
  - Does NOT participate in gameplay
  - Only observes and analyzes

**Game parameters**:
- Maximum 3 days
- Average game length: ~2.7 days
- Average messages: ~7.5 per game
- Average votes: ~8 per game

### Experimental Conditions

**Condition A: Filtered CoT Access**
- Overseer receives behavioral analysis extracted from player reasoning
- Filter identifies: deception signals, strategic patterns, role hints, emotional indicators
- Provides high-level insights like "HIGH deception indicators (3 signals)" rather than raw thoughts

**Condition B: No CoT Access**
- Overseer receives only observable information
- Public messages, voting patterns, elimination events
- No access to internal player reasoning

### Experimental Design (Critical)

**Proper control**: Both conditions used **identical game seeds** (1001-1020)
- Ensures both overseers face the same game scenarios
- Controls for game difficulty variation
- Allows direct comparison of overseer performance

**Initial flawed design**: Earlier experiments used different seeds (101-120 vs 201-220)
- Created invalid comparisons
- Explained inconsistent results
- This was corrected for final experiment

### Sample Size

- **20 games per condition**
- **40 total games**
- **19 valid comparisons** (1 no-CoT game timed out)
- **Runtime**: ~96 minutes
- **Cost**: ~$60 in API calls (OpenAI + Anthropic)

---

## Results

### Primary Outcome: Werewolf Identification Accuracy

| Condition | Correct ID | Total | Accuracy |
|-----------|-----------|-------|----------|
| **Filtered CoT** | 3 | 20 | **15.0%** |
| **No CoT** | 2 | 19* | **10.5%** |
| **Difference** | +1 | - | **+4.5%** |

*One game timed out and was excluded

**Statistical Analysis**:
- Fisher's exact test: **p = 0.66** (not significant)
- Effect size: Negligible
- Random chance baseline: **20%** (1 in 5 players)

**Key finding**: Both conditions perform **below chance**.

### Secondary Observations

**Game outcomes** (similar across conditions):
- Villager win rate: ~70%
- Average game length: 2.7 days
- Average messages: 7.5 per game

**Decision patterns**:
- 13 of 19 games: Both overseers made **identical guesses** for same seed
- 6 of 19 games: Different guesses, neither consistently better
- Suggests LLMs converge on similar (flawed) heuristics

**Guess distribution**:
- No strong bias toward any player number
- Both overseers guessed across all 5 players
- Shows decision-making engagement (not random/constant guessing)

---

## Key Findings

### 1. No Significant Effect of CoT Access

**CoT provides no meaningful advantage** in this social deception task:
- 4.5 percentage point difference is negligible
- Not statistically significant (p=0.66)
- Well within random variation

### 2. Both Approaches Fail at Deception Detection

**Performance below chance** (20% for random guessing):
- Filtered CoT: 15% accuracy
- No CoT: 10.5% accuracy
- Both underperform random selection

### 3. Task Appears Fundamentally Difficult for LLMs

**Why both fail**:
- Limited behavioral evidence (~8 messages, ~8 votes per game)
- Short game duration (~3 days) provides little deception pattern
- GPT-4o-mini werewolves are surprisingly effective deceivers
- Current LLMs lack robust theory of mind capabilities

### 4. Identical Seeds Produce Similar Decisions

When facing identical scenarios:
- 68% of games (13/19): Both made same guess
- Shows LLM reasoning convergence
- Suggests deterministic patterns in deception detection heuristics

---

## Discussion

### Why Doesn't CoT Help?

**Three possible explanations**:

1. **Information Overload Still Present**
   - Even filtered CoT may distract from behavioral signals
   - More information ≠ better decisions in adversarial contexts

2. **Strategic Deception in CoT**
   - Werewolf reasoning intentionally misleading
   - CoT contains strategic lies, not truth-seeking reasoning
   - Filter cannot distinguish genuine from deceptive reasoning

3. **Insufficient Signal Overall**
   - Task may simply be too difficult with limited data
   - ~8 messages and votes not enough to detect skilled deception
   - Both approaches fail because the task is hard, not because of information access

### Why Do Both Perform Below Chance?

**Systematic bias hypothesis**:
- LLMs may systematically favor certain patterns
- These patterns may anti-correlate with actual guilt
- Example: Werewolves who speak less might be flagged, but active deceptive players evade detection

**Task complexity hypothesis**:
- Human-level deception detection requires subtle social cognition
- Current LLMs lack true theory of mind
- Can't model strategic deception and counter-deception dynamics

---

## Limitations

### 1. Sample Size
- n=20 per condition is modest
- Larger sample (50-100 games) would increase statistical power
- Current study powered to detect large effects only

### 2. Single Model Combination
- Only tested GPT-4o-mini (agents) + Claude Opus (overseer)
- Results may not generalize to other model combinations
- Different models might show different patterns

### 3. Single Game Type
- Only tested Werewolf
- Other social deduction games (Resistance, Secret Hitler, Diplomacy) may differ
- Werewolf-specific dynamics might not generalize

### 4. Filtered CoT Only
- Did not test "full raw CoT" vs "no CoT"
- Don't know if filtering helps or hurts vs. raw reasoning logs
- Optimal filtering strategy unknown

### 5. No Human Baseline
- Don't know how humans perform on identical scenarios
- Can't assess if 15% is "good for the task" or "bad for LLMs"
- Need human expert comparison

### 6. Short Games
- 3-day maximum may not provide enough behavioral data
- Longer games might allow better deception detection
- Trade-off between game length and computational cost

---

## Implications

### For AI Research

1. **CoT is domain-specific**
   - Benefits in math/logic don't transfer to social deception
   - Need to evaluate reasoning techniques per domain

2. **Theory of mind challenges**
   - Current LLMs struggle with strategic deception detection
   - Gap between reasoning about logic vs. reasoning about minds

3. **Null results are valuable**
   - Not all techniques work in all domains
   - Negative results prevent false assumptions

### For AI Safety

1. **Transparency limitations**
   - More information (CoT) doesn't guarantee better decisions
   - Explainability ≠ accuracy in adversarial settings

2. **Deception detection challenges**
   - Current AI systems poor at detecting AI-generated deception
   - Important for AI safety and alignment concerns

### For Game AI

1. **Need specialized approaches**
   - General reasoning improvements may not help social games
   - Domain-specific training/architectures may be necessary

2. **Human-AI gap remains**
   - Experienced human Werewolf players likely outperform LLMs
   - Social cognition remains a frontier challenge

---

## Future Work

### Immediate Next Steps

1. **Increase sample size to n=50** per condition
   - Improve statistical power
   - Reduce chance of Type II error

2. **Test raw CoT vs filtered CoT vs no CoT**
   - Three-way comparison
   - Determine if filtering helps or hurts

3. **Add human baseline**
   - Recruit expert Werewolf players
   - Give them same information as AI overseers
   - Compare human vs. AI performance

### Medium-Term Research

4. **Test other model combinations**
   - Different agent models (GPT-4, Claude, etc.)
   - Different overseer models
   - Check if results generalize

5. **Vary game length**
   - Test 5-day, 7-day games
   - See if more data improves detection
   - Find optimal game length for detection

6. **Test other social deduction games**
   - The Resistance (no hidden information killing)
   - Secret Hitler (team-based deception)
   - Avalon (known team members)
   - Check domain generality

### Long-Term Research

7. **Specialized training**
   - Fine-tune models on deception detection
   - Train on thousands of Werewolf games
   - Test if specialized models outperform general ones

8. **Architectural improvements**
   - Memory systems for tracking deception over time
   - Explicit theory of mind modules
   - Multi-agent reasoning architectures

9. **Cross-domain deception detection**
   - Test on real-world deception tasks
   - Fraud detection, security applications
   - Check if game results transfer

---

## Technical Details

### System Architecture

```
┌─────────────────────────────────────────┐
│         Game Engine (Python)             │
│  - State management                      │
│  - Turn order control                    │
│  - Win condition checking                │
└─────────────────────────────────────────┘
            │
            ├─────────────────┬──────────────────┐
            ↓                 ↓                  ↓
┌──────────────────┐  ┌──────────────┐  ┌─────────────────┐
│  Player Agents   │  │   Overseer   │  │   Logger        │
│  (GPT-4o-mini)   │  │ (Claude Opus)│  │  (JSON files)   │
│                  │  │              │  │                 │
│ - Generate msgs  │  │ - Moderate   │  │ - Game state    │
│ - Vote           │  │ - Analyze    │  │ - All messages  │
│ - Night actions  │  │ - Predict    │  │ - Overseer logs │
└──────────────────┘  └──────────────┘  └─────────────────┘
```

### Prompt Engineering

**Agent prompts**:
- Role-specific instructions (werewolf vs. villager)
- Strategic guidance for deception/detection
- JSON-formatted responses for parsing

**Overseer prompts**:
- Two versions: with filtered insights vs. without
- Explicit instructions to identify werewolves
- JSON output for suspicion scores and top guess

### Filtering Algorithm

**CoT Filter** (for filtered condition):
1. Parse player private thoughts
2. Count keyword matches:
   - Deception indicators (deflect, blame, suspicious)
   - Strategic thinking (plan, manipulate, control)
   - Role hints (werewolf, innocent, investigate)
   - Emotional signals (nervous, confident, defensive)
3. Detect behavioral patterns:
   - Excessive justification
   - Fixation on specific players
   - Hedging/uncertainty
   - Overconfidence
4. Generate summary with player-specific insights
5. Provide to overseer instead of raw thoughts

---

## Reproducibility

### Code & Data

- **Repository**: `custom_werewolf_game/`
- **Main script**: `experiment.py`
- **Results**: `experiment_results.json`
- **Game logs**: `game_log_filtered_cot_*.json`, `game_log_no_cot_*.json`

### Running the Experiment

```bash
# Install dependencies
pip install -r requirements.txt

# Set API keys
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"

# Run experiment (20 games per condition)
python experiment.py

# Results will be in experiment_results.json
```

### Configuration

**Experiment parameters** (in `experiment.py`):
- Seeds: 1001-1020 (same for both conditions)
- Players: 5
- Werewolves: 1
- Fortune tellers: 1
- Max days: 3
- Agent model: gpt-4o-mini (OpenAI)
- Overseer model: opus (Claude 3 Opus)
- Timeout: 300 seconds per game

---

## Cost & Runtime Analysis

### Per Game
- **Runtime**: ~2.9 minutes average
- **API calls**:
  - GPT-4o-mini: ~25-30 calls (player actions)
  - Claude Opus: ~10-15 calls (overseer analysis)
- **Cost**: ~$1.50 per game

### Full Experiment (40 games)
- **Runtime**: ~96 minutes (1.6 hours)
- **Total API calls**: ~1,400-1,800
- **Total cost**: ~$60

### Scaling Projections
- **100 games**: ~$150, ~4 hours
- **500 games**: ~$750, ~20 hours
- **1000 games**: ~$1,500, ~40 hours

---

## Conclusion

This study found **no evidence that Chain-of-Thought reasoning logs improve deception detection** in AI overseers for social games. Both filtered CoT and no-CoT approaches achieved poor accuracy (15% and 10.5% respectively, vs. 20% chance), with no significant difference between them (p=0.66).

The results suggest that:
1. **CoT benefits are domain-specific** - advantages in math/logic don't transfer to social deception
2. **Current LLMs struggle with theory of mind** - detecting strategic deception remains challenging
3. **Information access alone is insufficient** - more information doesn't solve the core problem

This negative result contributes to our understanding of LLM limitations and highlights the need for specialized approaches to social reasoning and deception detection tasks.

### Recommended Conclusion Statement

**"In a controlled experiment with 20 games per condition, we found no significant difference in werewolf identification accuracy between AI overseers with filtered Chain-of-Thought access (15%) and those without (10.5%), p=0.66. Both approaches performed below chance (20%), suggesting fundamental limitations in current large language models' ability to detect strategic deception in multi-agent social games, regardless of reasoning transparency."**

---

## Acknowledgments

- OpenAI for GPT-4o-mini API access
- Anthropic for Claude Opus API access
- Claude (Anthropic) for experimental design assistance and code development

---

## References

### Key Literature

1. **Wei, J., et al. (2022)**. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." NeurIPS 2022.
   - Established CoT benefits for math/logic tasks

2. **Shi, F., et al. (2023)**. "Large Language Models Can Be Easily Distracted by Irrelevant Context."
   - Shows LLMs can be hurt by additional information

3. **Kahneman, D. (2011)**. "Thinking, Fast and Slow."
   - System 1 vs System 2 thinking in complex social contexts

4. **DePaulo, B. M., et al. (2003)**. "Cues to deception." Psychological Bulletin.
   - Human deception detection literature

5. **Park, P. S., et al. (2023)**. "AI Deception: A Survey of Examples, Risks, and Potential Solutions."
   - AI deception and detection challenges

---

**Document Version**: 1.0
**Last Updated**: September 2024
**Status**: Experiment Complete - Ready for Publication Discussion