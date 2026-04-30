---
type: experiment-design
status: in-progress
started: 2026-04-29
---

# Experiment: Chain-of-Thought Mechanism Analysis

## Research Question

Does the model in Group C *verbalize* the attempt count signal in its reasoning, or does the signal act as implicit anchoring without conscious use?

Two hypotheses:

**H1 — Cognitive (explicit):** The model explicitly references the attempt count in its internal reasoning text ("I'm on attempt 1 of 5, I should commit quickly"). Effect is mediated by conscious resource awareness.

**H2 — Anchoring (implicit):** The model never mentions the signal but still acts differently. The `[attempt: 1/5]` acts as a low-level nudge without verbalization — similar to priming effects in psychology.

**Why it matters:**
- If H1: the mechanism is deliberate planning → E1/E2 (degraded context) makes sense because the explicit signal replaces lost implicit context
- If H2: the mechanism is anchoring → E1/E2 design needs rethinking (anchoring may not require degraded context to work)

## Design

**Groups to compare:** A (control), C (count signal), D (instruction only)

**n per group:** 15 problems (Python/0-14, same as main experiment)

**What we capture:** Full stream-JSON output including all TEXT events (model's visible reasoning before each tool call)

**Analysis:**
1. Extract all TEXT blocks from each session
2. Search for explicit mentions of: "attempt", "1 of 5", "budget", "tries", "remaining", time-related words
3. Compare mention frequency: A vs C vs D
4. Qualitative read of full reasoning chains for representative problems

## Expected outputs

- `results/cot_group_A_*.jsonl` — reasoning text per problem
- `results/cot_group_C_*.jsonl`
- `results/cot_group_D_*.jsonl`
- `wiki/experiment/cot_findings.md` — findings and interpretation

## Metrics

| Metric | Description |
|---|---|
| mention_rate | % of sessions where model explicitly mentions attempt/budget/tries |
| first_mention_turn | Which turn (1st, 2nd...) the signal is first verbalized |
| avg_text_length | Length of reasoning blocks (longer = more deliberate planning?) |
| strategy_words | Frequency of "different approach", "try instead", "alternatively" |

## Connection to main paper

Results go into a new subsection of Discussion: "Mechanistic Evidence". If H1 is supported, strengthens the CoALA metareasoning interpretation. If H2, opens a new line of inquiry around anchoring effects in LLM agents.
