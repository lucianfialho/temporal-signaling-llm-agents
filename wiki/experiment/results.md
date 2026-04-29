# Experiment Results

## Overview

Two experiments were run, using two different Claude models: Claude Sonnet (claude-sonnet) and Claude Opus (claude-opus). The core finding is that **temporal signals have opposite effects depending on model capability**: attempt count makes Sonnet more efficient (fewer tool-use turns), while any temporal signal makes Opus more exploratory (more tool-use turns).

---

## Groups

| Group | Signal injected | Description |
|---|---|---|
| A | None | Control — no temporal signal |
| B | `session_elapsed: Xs` + `attempt: N/5` + efficiency instruction | Full temporal signal (time + count + instruction) |
| C | `attempt: N/5` only | Attempt count only |

---

## Full Results Table

### Claude Sonnet (n=100 per group)

| Group | Mean turns | SD | vs. A (p-value) | Significance | Cohen d | Delta (A − group) |
|---|---|---|---|---|---|---|
| A (control) | 7.10 | — | — | — | — | — |
| B | 7.02 | — | p=0.52 | ns | — | +0.08 |
| C | 6.49 | — | p=0.003 | ** | ~0.62 | +0.61 |

**B vs. C:** p=0.039 *

### Claude Opus (n=50 per group)

| Group | Mean turns | SD | vs. A (p-value) | Significance | Cohen d | Delta (A − group) |
|---|---|---|---|---|---|---|
| A (control) | 7.62 | — | — | — | — | — |
| B | 8.26 | — | p=0.012 | * | −0.44 | −0.64 |
| C | 8.14 | — | p=0.097 | ns | −0.36 | −0.52 |

**B vs. C:** p=0.49 ns

Note: For Opus, delta is reported as A − group; negative values mean the group uses MORE turns than control.

---

## Statistical Tests

- **Solve rate:** Fisher's exact test (binary pass/fail). Solve rate was statistically identical across all groups and both models (~98–100%).
- **Tool-use turns:** Mann-Whitney U test (non-parametric; turns counts are non-normal). Alpha = 0.05.
- **Effect size:** Cohen d (via rank-biserial correlation for Mann-Whitney).

---

## Pairwise Summary

| Comparison | Sonnet p | Sonnet result | Opus p | Opus result |
|---|---|---|---|---|
| A vs. C (attempt count only) | 0.003 ** | C uses FEWER turns | 0.097 ns | No significant difference |
| A vs. B (time + count) | 0.52 ns | No significant difference | 0.012 * | B uses MORE turns |
| B vs. C | 0.039 * | C < B | 0.49 ns | No significant difference |

---

## Interpretation

### Sonnet: attempt count induces efficiency

For Sonnet, Group C (attempt count only) uses significantly fewer tool-use turns than the control (p=0.003, medium-to-large effect). Group B (count + elapsed time) does not differ from control — the elapsed-time signal cancels the efficiency gain. This replicates and strengthens the original finding: discrete attempt count is the operative signal; continuous elapsed time adds noise.

### Opus: temporal signals induce exploration

For Opus, the effect is reversed. Group B (count + elapsed time) uses significantly MORE turns than control (p=0.012, d=−0.44). Group C (count only) also trends toward more turns but does not reach significance (p=0.097). Opus already uses more turns at baseline (7.62 vs. 7.10 for Sonnet). The additional turns in Groups B and C likely reflect more thorough exploration — Opus may be using the temporal signal to justify deeper investigation rather than to constrain effort.

### The capability interaction

The opposing direction of effect across models is the primary finding of the two-experiment series. A plausible mechanism:

- **Less capable models (Sonnet):** The attempt count acts as a convergence cue — "you have limited budget, commit to a fix." This reduces exploratory tool calls.
- **More capable models (Opus):** The attempt count may act as a license for thoroughness — "I still have budget, I should be comprehensive." Opus also has a higher intrinsic tendency toward multi-step reasoning, so the signal may amplify rather than constrain that tendency.

This is consistent with the **metareasoning gap** identified in CoALA: more capable agents may adaptively allocate more computation in response to budget information, not less.

---

## Key Numbers for Paper

- Sonnet A vs. C: p=0.003, **d≈0.62**, Δ=−0.61 turns (C uses fewer)
- Opus A vs. B: p=0.012, d=−0.44, Δ=−0.64 turns (B uses MORE)
- Solve rate: not significant in any comparison, both models

---

## See Also

- [Attempt Budgets](../concepts/attempt_budget.md) — Conceptual framing, cognitive psychology analogies, literature review.
- [Paper Draft Outline](../paper_draft/outline.md) — Working outline including the new model-capability section.
