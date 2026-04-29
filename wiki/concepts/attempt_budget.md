# Attempt Budgets in LLM Agents

## Definition

An **attempt budget** is the explicit communication to an LLM agent of both its current iteration count and the maximum number of iterations available: `attempt: N/MAX`. The agent knows not only *where it is* in a task sequence but *how much of its budget remains*.

This is distinct from:
- A hard loop limit enforced externally (the system stops the agent at N=MAX regardless of agent state).
- An implicit iteration count derivable from conversation history length.
- A soft stopping criterion based on output quality (as in Self-Refine's per-aspect quality scores).

An attempt budget is explicit, injected into the agent's context, and leaves the interpretation to the model. The agent can in principle ignore it, use it to accelerate, use it to be more conservative, or use it to change tool-use strategy. Our experiment tests which of these actually occurs.

---

## Analogy: Deadline Effects in Cognitive Psychology

The most well-known cognitive analogue is **Parkinson's Law**: "Work expands so as to fill the time available for its completion" (Parkinson, 1955). The agent analogue would be that without a stated budget, the agent uses as many turns as it can, exploring suboptimal paths it would abandon if it knew the budget was limited.

Several related effects from the deadline literature are relevant:

**Deadline effects / time pressure:** Research on human problem-solving under time constraints (Svenson & Maule, 1993; Payne, Bettman & Johnson, 1988) consistently shows that constrained actors adopt *more heuristic*, *less exhaustive* search strategies. They switch from compensatory to non-compensatory decision rules — they stop gathering marginal information. In our context: fewer tool-use turns per attempt when the agent knows the budget is tight.

**Goal-gradient effect:** Agents accelerate as they approach a goal (Hull, 1932; Kivetz, Urminsky & Zheng, 2006). Knowing "this is attempt 4 of 5" creates a gradient that should increase commitment to the current approach and reduce exploratory tool calls.

**The planning fallacy inverse:** When no deadline is stated, agents (human and artificial) tend to underestimate effort requirements and over-plan. An explicit budget may counteract this by anchoring expected effort.

**Caveat — Parkinson's Law as inflation, not quality:** Parkinson's Law predicts that without budget constraints, work *inflates* but quality does not improve. This is exactly our null result for solve rate: Group C agents use fewer tool-use turns than Group A, but solve the same proportion of problems. The reduction is pure efficiency gain, not a quality tradeoff.

---

## What the Literature Says

### Self-Refine (arXiv:2303.17651)

Self-Refine uses a fixed maximum iteration count (4) as its stopping criterion. The paper demonstrates:

- **Diminishing returns by iteration:** The largest quality gain occurs at iteration 1→2. By iteration 3, marginal improvement is small but positive. This implies that agents *could* achieve most of the gain in fewer iterations if they knew the budget was constrained — consistent with attempt budgets inducing more efficient behavior.
- **The math failure case:** When external feedback is unavailable (math reasoning), the model reports "everything looks good" 94% of the time. Attempt budget alone cannot substitute for a meaningful stopping signal — the agent must perceive failure. This is a boundary condition for our finding: attempt budgets likely work only when the agent can detect per-attempt success/failure (which is true in debugging via test execution).
- **Iteration count as the sole temporal variable:** Self-Refine never tracks elapsed time; discrete iteration count is the only temporal dimension. The paper implicitly validates attempt count as the natural unit for iterative agent loops.

### CoALA (arXiv:2309.02427)

CoALA explicitly identifies **metareasoning** — the adaptive allocation of compute to planning — as a critical unsolved problem:

> "Most LLM reasoning methods fix a search budget by specifying a depth of reasoning, but humans appear to adaptively allocate computation."

An attempt budget is a mechanism for injecting exactly this adaptive capacity: the agent is given the information needed to reason about how much search is appropriate given remaining budget. CoALA predicts that agents with this information should produce better-calibrated action proposals — specifically, they should converge on a grounding action (submitting a fix) with fewer intermediate cycles.

CoALA also identifies attempt count as a natural **working memory variable**: it persists across decision cycles, is small (a single integer), and conditions the agent's planning horizon. Working memory in CoALA is the hub that connects perception (tool outputs) to planning (what to do next); attempt count slots naturally into this role.

### MemGPT (arXiv:2310.08560)

MemGPT's memory-pressure warnings provide a structural analogue to attempt budgets. When the FIFO message queue nears its token limit, MemGPT sends an automatic warning ("context window is N% full") that changes agent behavior — it starts archiving content rather than generating responses. This is functionally equivalent to an attempt budget signal: "you are running low, change strategy."

The nested KV retrieval results show that agents with explicit state tracking (how many retrieval hops have been taken) outperform agents without this tracking. This supports the general principle that discrete counts of prior interactions — not continuous time — are the operationally relevant signal for agentic loops.

MemGPT does not study attempt count as an independent variable, and its recursive summary mechanism means that attempt history degrades lossily over time — a limitation our experiment addresses by providing an explicit, lossless count.

### Episodic Memory (arXiv:2502.06975)

The episodic memory framing provides a theoretical bridge. Each debugging attempt is an **episode**: a single-shot, instance-specific event with contextual bindings (which tools were used, what the test output was, what edit was made). The episodic memory paper argues that the "when" dimension of episodic memory is fundamentally ordinal — what matters is the position of an episode in a sequence, not its calendar timestamp.

An attempt budget makes the ordinal position explicit (`attempt: N/MAX`), which the episodic memory framework predicts should improve retrieval of relevant prior episodes ("what did I try in attempt N-1?") and planning ("given I have MAX-N attempts left, how should I allocate effort?").

The paper's consolidation roadmap is also relevant: with repeated exposure to the same bug patterns, agents should consolidate episodic instances into procedural shortcuts — fewer tool-use turns on later attempts of similar bugs. Our experiment captures a short-run analogue (within a single session), not the long-run consolidation effect.

---

## Our Finding

**Temporal signals have opposite effects on tool-use turns depending on model capability. Solve rate is unaffected in both models.**

### Claude Sonnet Results (n=100/group)

| Group | Signal | Solve Rate | Tool-Use Turns (mean) | vs. Control |
|---|---|---|---|---|
| A (control) | None | ~98–100% | 7.10 | — |
| B | `session_elapsed: Xs` + `attempt: N/5` + system prompt | ~98–100% | 7.02 | p=0.52 ns |
| C | `attempt: N/5` only | ~98–100% | 6.49 | p=0.003 **, d≈0.62 |

**B vs. C:** p=0.039 *

For Sonnet, the key finding is the asymmetry between Groups B and C. Attempt count alone (Group C) reduces turns significantly. Adding elapsed time (Group B) eliminates the benefit — suggesting elapsed time is not a neutral addition but introduces noise that cancels the count signal.

The mechanism is most consistent with the **noise hypothesis**: the agent must jointly interpret two temporal signals, one tractable (count) and one not (elapsed time). The attention required to process the elapsed-time token may dilute the weight given to the count token, or the agent may attempt to jointly condition its plan on both signals, producing a suboptimal mixture.

Cohen d≈0.62 is a medium-to-large effect for a single-variable prompt intervention. This is practically significant: the agent completes the same set of tasks using measurably fewer tool calls, which translates directly to lower inference cost and shorter time-to-completion in real deployments.

### Claude Opus Results (n=50/group)

| Group | Signal | Solve Rate | Tool-Use Turns (mean) | vs. Control |
|---|---|---|---|---|
| A (control) | None | ~98–100% | 7.62 | — |
| B | `session_elapsed: Xs` + `attempt: N/5` + system prompt | ~98–100% | 8.26 | p=0.012 *, d=−0.44 |
| C | `attempt: N/5` only | ~98–100% | 8.14 | p=0.097 ns |

**B vs. C:** p=0.49 ns

For Opus, the direction is reversed: temporal signals *increase* tool-use turns rather than decreasing them. Group B is significantly higher than control (p=0.012); Group C trends in the same direction. Opus already uses more turns at baseline (7.62 vs. 7.10 for Sonnet), suggesting its default planning style is more exploratory. Temporal signals appear to amplify this tendency rather than constrain it.

### Model-Capability Interaction

The key theoretical insight is that **model capability moderates the direction of the temporal signal effect**:

- **Less capable models (Sonnet):** Attempt count acts as a convergence cue — "you have limited budget, commit to a fix." This prunes exploratory tool calls.
- **More capable models (Opus):** Attempt count may act as a license for thoroughness — "I have budget, I should be comprehensive." Opus has the capacity to make additional turns productive.

This is consistent with the CoALA metareasoning gap: adaptive compute allocation looks different at different capability levels. A model that can genuinely use more reasoning steps productively will do so when given budget information; a model that cannot will instead streamline.

Note: "more turns" in Opus is not necessarily worse if the additional turns yield higher-quality or more thorough fixes. Whether Opus's exploratory behavior improves output quality beyond what the test oracle captures is an open question.

---

## Open Questions

1. **Does the MAX denominator matter?** We used N/5. Does N/3 (more urgency) or N/10 (less urgency) produce different effects? Parkinson's Law and the goal-gradient effect predict that lower remaining budget fractions should produce greater efficiency gains for Sonnet. For Opus, a tighter denominator might flip the direction back toward efficiency.

2. **Does attempt budget help more on hard problems than easy ones?** If the efficiency gain (Sonnet) comes from pruning exploratory tool calls, we would expect larger effects on problems where the naive agent over-explores. Easy problems may show no effect; hard problems may show the largest reductions.

3. **What is the boundary condition for solve rate?** We found no solve rate change in either model, but our problems were solvable by Group A agents ~98–100% of the time. If Group A solve rate were lower (harder problems), would Group C's efficiency-seeking behavior trade solve rate for speed (for Sonnet), or would Opus's exploration actually improve solve rate?

4. **Does the system prompt instruction matter independently?** Group B received both the attempt count *and* an explicit system prompt instructing the agent to use time wisely. Group C received only the count. We cannot separate the effect of the instruction from the effect of the elapsed-time signal in Group B. A Group D (instruction only, no signals) would isolate this.

5. **Where is the capability threshold?** Sonnet and Opus represent two points on the capability spectrum. At what capability level does the effect direction switch? Testing Haiku (lower capability) and intermediate models would map this curve.

6. **Does Opus's exploratory behavior improve quality?** More turns in Opus does not necessarily mean worse outcomes. Qualitative analysis of tool call content, or testing on problems with stricter pass criteria, would determine whether Opus's additional turns are productive or redundant.

7. **Generalization across model families:** The Sonnet/Opus comparison is within Anthropic's Claude family. Would a GPT-4o vs. GPT-4o-mini comparison show the same pattern? Replication with open-source models (Llama 3, Mistral) at different capability tiers would test whether this is a capability effect or an Anthropic-training artifact.

---

## See Also

- [Temporal Signaling in LLM Agents](temporal_signaling.md) — Broader taxonomy of signal types.
- `../paper_draft/outline.md` — Working outline for the preprint.
