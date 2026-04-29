# Discussion

## Why Attempt Count Helps Sonnet

The efficiency gain in Sonnet's Group C is consistent with the metareasoning gap identified by Sumers et al. (2023): agents without a budget signal allocate tool-use turns as if each attempt were the first. When the agent knows it is on attempt 1 of 5, it has a concrete stopping criterion that is absent in the control condition. Rather than exploring multiple diagnostic hypotheses in sequence — reading the code, running the tests, forming a theory, applying a fix, re-reading if it fails — the agent appears to converge on a fix earlier, accepting higher uncertainty in its hypothesis and committing to an edit sooner.

This is consistent with Self-Refine's diminishing-returns curve (Madaan et al., 2023): the largest gain from iteration occurs at step 1→2, because that is when the agent's uncertainty is highest. An attempt count signal short-circuits unnecessary early-turn exploration by signaling that the current attempt is one of several available — a form of Bayesian updating on available resources.

Critically, the effect is on *efficiency* (turns), not *accuracy* (solve rate). The agent does not solve more problems — it solves them with less effort. This rules out the hypothesis that attempt count provides task-relevant information. Instead, it provides a resource signal that calibrates planning depth.

## Why Elapsed Time Does Not Help — And May Add Noise

For Sonnet, Group B (time + attempt) performed no better than the control despite including the same attempt count as Group C. The most parsimonious explanation is interference: the elapsed time signal adds context that the model must process, and that processing consumes reasoning capacity that would otherwise go toward the debugging task. The model attends to the time value, attempts to interpret its significance, and produces a slightly noisier action plan — canceling the benefit of the count signal.

This is consistent with the temporal reasoning literature. LoCoMo (Maharana et al., 2024) shows that LLMs underperform on elapsed-time questions by 73 percentage points relative to humans. Alonso et al. (2024) find that semantic retrieval over timestamps achieves 3–6% recall, while ordinal session-number retrieval achieves 90%. If the model cannot reliably reason about elapsed time in comprehension tasks, it is unlikely to use it productively as a planning signal in an action loop. The time value becomes noise rather than signal.

## Why Opus Responds Differently

The reversal in Opus — where temporal signals *increase* tool-use turns — suggests a different mechanism. Opus, as a more capable model, may treat the attempt-count or time signal not as a resource constraint but as an invitation to be more thorough. Where Sonnet reads "attempt 1/5" as *commit sooner*, Opus may read it as *you have 4 more tries if this one fails, so explore now*.

This is a form of the explore-exploit tradeoff applied to debugging. A more capable model with a higher baseline confidence in its reasoning may rationally allocate more turns to exploration when it knows retries are available — the opposite of what a less confident model does. The result is more turns per trial, but with identical solve rate, suggesting the extra turns are spent on verification and hypothesis enumeration rather than on finding the fix itself.

This interpretation is speculative; we cannot observe the agent's internal reasoning directly. But it is consistent with Opus's higher baseline turn count (7.62 vs. Sonnet's 7.10 in the control) and with the literature on capability-dependent self-refinement: Madaan et al. (2023) note that weaker models cannot reliably detect their own failures, and their self-feedback adds noise rather than signal. The inverse may hold for frontier models: stronger models detect success earlier and use additional context to explore more thoroughly before committing.

## Practical Implications

Three recommendations follow from these results for practitioners building LLM agent systems:

**1. Inject attempt count, not elapsed time.** Attempt count is a three-token addition to the prompt (`[attempt: N/M]`) with no computational cost. For mid-tier models, it reduces tool-use turns — and by extension, API costs and latency — without affecting task success. Elapsed time provides no benefit and may introduce noise.

**2. Calibrate by model tier.** The effect direction reverses between Sonnet and Opus. A system prompt optimized for efficiency with Sonnet may increase turn count with Opus. Agent harness designers should treat temporal signal configuration as a model-specific hyperparameter, not a universal default.

**3. Solve rate is not the right metric for efficiency studies.** All conditions converged to the same solve rate, but tool-use turns varied by up to 10% between groups. Cost and latency optimization in deployed agents requires measuring turns or token counts directly, not just pass/fail outcomes.
