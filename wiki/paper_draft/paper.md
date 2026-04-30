# Attempt Count, Not Elapsed Time, Reduces Tool-Use Turns in LLM Debugging Agents

**Lucian Fialho**  
Independent Researcher  
lucian@metricasboss.com.br

---

# Abstract

LLM agents in iterative loops have no built-in sense of how many attempts they have made. We ask whether injecting this information changes debugging efficiency — and whether the effect depends on model capability.

We ran a controlled experiment on HumanEvalPack Python bugs using Claude Code as the agent, testing four conditions: no temporal signal (control, Group A), elapsed time + attempt count (Group B), attempt count alone (Group C), and instruction framing without any signal (Group D, ablation). We replicated across two model tiers: Sonnet (n=100/group, two independent runs) and Opus (n=50/group, one run).

Solve rate was identical across all groups (~98–100%). For Sonnet, Group C used significantly fewer tool-use turns than control (p=0.003, Cohen d=0.45); Group D (instruction without signal) did not (p=0.29 ns), establishing the count signal as the causally active element. For Opus, Group B used significantly more turns than control (p=0.012, d=0.44), with Group C trending similarly (p=0.097).

A chain-of-thought analysis (n=15/group) found that 93% of Group C sessions never verbalized the attempt count, yet produced 20% shorter reasoning text — consistent with implicit anchoring rather than explicit metareasoning.

We conclude that attempt count is a low-cost signal with model-dependent effects: it induces efficiency in mid-tier models, apparently through anchoring, while frontier models show increased exploratory behavior under the full temporal signal (Group B). To our knowledge, this is the first controlled study isolating elapsed time vs. attempt count as agent planning signals, and the first to show that the effect direction depends on model capability.

---

# Introduction

LLM-based agents deployed on iterative tasks — debugging, code generation, tool use — operate without any built-in sense of how long they have been working or how many attempts they have made. Each turn in the agent loop is processed with the same context as the first. This is not a fundamental limitation of the architecture, but a design choice: the harness simply does not inject this information.

The question we ask is whether it should. Temporal context is cheap to compute and trivial to inject. If it changes agent behavior in useful ways — reducing wasted effort, triggering strategy shifts — the cost-benefit is obvious. If it does not, that too is worth knowing.

We designed a controlled experiment around this question. Using Claude Code as the agent on HumanEvalPack Python debugging problems, we compared four conditions: a control with no temporal signal (Group A), a treatment with elapsed time and attempt count (Group B), attempt count alone (Group C), and a post-hoc instruction ablation with no temporal signal (Group D). We replicated across two model tiers — Sonnet and Opus — to test whether any effect is model-dependent.

The results were unexpected. Solve rate was identical across all conditions. But the effect on tool-use turns diverged sharply by model: Sonnet became more efficient with attempt count, Opus became more exploratory with the full temporal signal. The same prompt prefix produced opposite efficiency effects depending on model capability: for Sonnet, attempt count (Group C) reduced turns; for Opus, the full signal (Group B) increased turns. The conditions that reached significance differed by model tier.

This paper makes three contributions: (1) to our knowledge, the first controlled experiment isolating elapsed time vs. attempt count as agent context signals; (2) evidence that model capability moderates the direction of the effect; (3) a practical recommendation for agent system designers — inject attempt count, and calibrate expectations by model tier.

---

# Related Work

Our experiment sits at the intersection of three research streams that have not previously been connected: iterative refinement in LLM agents, temporal reasoning in language models, and memory architecture for long-horizon agents. A fourth adjacent stream — budget-aware prompting — is most closely related but addresses a different level of the problem.

## Iterative Refinement

Self-Refine (Madaan et al., 2023) is the closest structural analogue to our setup. The paper shows that an LLM iterating over its own output with explicit feedback improves quality by 5–49% across seven tasks — with most gain occurring at iteration 1→2 and diminishing returns thereafter. Two findings are directly relevant. First, the diminishing-returns curve implies that the agent's uncertainty about what to try is highest at the first iteration and decreases with each attempt — a mechanism that attempt count could encode. Second, math reasoning (a domain with unambiguous pass/fail oracles) shows near-zero gain from self-refinement because the model cannot reliably detect its own failures. Our debugging setup avoids this failure mode: test output provides unambiguous feedback each turn.

The Cognitive Architectures for Language Agents (CoALA) framework (Sumers et al., 2023) provides the theoretical grounding. CoALA identifies *metareasoning* — adaptive allocation of compute based on task progress — as a critical open problem. Current agents fix a search budget rather than inferring when to stop or change strategy. Attempt count is precisely a metareasoning signal: it encodes how many planning cycles have elapsed, enabling the agent to modulate its decision-making accordingly. Critically, CoALA's decision cycle is driven by observations from grounding actions, not by wall-clock time. Attempt count maps naturally onto the agent's internal cycle count; elapsed time does not appear anywhere in the standard action-observation loop.

## Temporal Reasoning in LLMs

A consistent finding across multiple benchmarks is that LLMs reason poorly about continuous time. LoCoMo (Maharana et al., 2024), a long-term conversational memory benchmark, finds that temporal reasoning is the hardest category for all tested architectures — long-context models score ~20% F1 on temporal questions versus 93% for humans, a 73-point gap that exceeds the average gap on other question types. This is not surprising: wall-clock time is a continuous scalar that the model must represent implicitly, with no dedicated encoding.

Discrete event identifiers are more tractable. Alonso et al. (2024) show that semantic retrieval over conversational memory achieves 3–6% recall on time-based queries ("what did we discuss last Tuesday?") but jumps to 90% recall when a tabular lookup on session index is used instead. Session number — an ordinal integer — is the most reliably retrievable temporal unit in their experiments. This is the retrieval-side analogue of our main finding: discrete count outperforms continuous time as an LLM-accessible signal, whether for retrieval or for planning.

Time-Sensitive Question Answering benchmarks (Yang et al., 2024) further document that LLMs underperform on questions requiring elapsed-time reasoning and that performance degrades faster with temporal distance than with semantic distance. Jang et al. (2023) show that models trained with explicit time-interval labels produce more contextually appropriate responses than models without, but only when the interval is expressed as a discrete category ("a few weeks later") rather than a precise timestamp. Together, these results suggest that the tractable unit of temporal reasoning for LLMs is the discrete event or interval category, not the continuous timestamp.

## Memory Architecture

MemGPT (Packer et al., 2023) and the Episodic Memory framework (Pink et al., 2025) converge on a similar architectural principle from different angles. MemGPT treats memory as a paged hierarchy: working memory, external memory, and archival storage are managed via explicit function calls. The agent tracks its position in a task not by elapsed time but by operation count — how many retrieval, read, and write calls it has issued. This is structurally identical to attempt count in a debugging agent.

Episodic memory theory (Pink et al., 2025) identifies five properties that distinguish episodic from other memory types, including *contextual relations* — encoding when, where, and who, with temporal order as a primary retrieval dimension. The paper argues that ordinal position (which episode was this?) is the tractable episodic index, not wall-clock time. A failed debugging attempt is an episode in this sense; knowing it was attempt N-1 provides more actionable context than knowing it happened 47 seconds ago.

## Budget-Aware Prompting

The most adjacent work is TALE (Han et al., 2024), which injects a token budget into chain-of-thought prompts ("let's think step by step and use less than N tokens"). TALE shows that including a token budget reduces CoT output length by 68% on average while maintaining accuracy within 5%. The mechanism is directly analogous to our attempt count signal: both provide a resource constraint that the model uses to calibrate planning depth.

The critical distinction is the level of operation. TALE measures output token counts in single-call reasoning tasks (math, logical inference). Our work measures tool-use turns in multi-step agentic loops with external tool execution and pass/fail test oracles. A token budget and an attempt count budget operate on different computational primitives: one constrains reasoning verbosity within a single inference call; the other constrains action selection across an iterative agent loop. TALE does not study temporal signals, elapsed time, multi-model effects, or agentic tool use. Our finding that the direction of effect depends on model capability has no analogue in the TALE results.

## Practitioner Implementations

Independent of the academic literature, practitioners have begun implementing iteration budget signals in production agent harnesses — confirming the intuition that motivates this paper, and underscoring the absence of empirical evidence.

TraceCoder (Rorseth et al., 2025), a multi-agent debugging framework, informs the repair agent how many cycles have been executed and how many remain before each turn. Pass@1 accuracy improves consistently as max attempts increases, but the paper treats attempt count as an architectural parameter, not an experimental variable. No controlled comparison with a no-count baseline is reported.

An open feature request in the hermes-agent harness (NousResearch, 2025) proposes a two-tier "iteration budget pressure" system: a caution message injected at 70% of max iterations ("start consolidating your work") and a warning at 90% ("provide your final response NOW"). The proposal is motivated by observed failure modes where agents silently exhaust iterations making tool calls without producing a substantive response. The feature remains unmerged at the time of writing, and no effectiveness data has been reported.

LiteLLM implements iteration budgets as a hard server-side cap (HTTP 429 after N calls) rather than a context injection — a gating mechanism, not a planning signal.

These implementations collectively demonstrate that the practitioner community has identified the need for attempt-aware agents. To our knowledge, our experiment is the first to study this systematically: isolating the causal effect of attempt count injection, comparing it against elapsed time, measuring the outcome on a controlled benchmark, and testing whether the effect generalizes across model tiers.

## Gap Addressed by This Work

None of the prior work directly manipulates temporal signals as independent variables in a tool-using agent setting with a pass/fail oracle. Self-Refine does not track elapsed time or attempt count as a context variable. CoALA identifies metareasoning as a gap but offers no empirical test. The temporal reasoning and memory papers study retrieval quality and comprehension, not downstream agent behavior in an action loop. TALE establishes that budget signals affect single-call reasoning, but does not study agentic loops, tool use, temporal signals, or cross-model effects. TraceCoder and hermes-agent confirm practitioner demand but provide no controlled measurements. To our knowledge, our experiment is the first to isolate elapsed time vs. attempt count in a controlled, agentic debugging task — and the first to show that the effect direction depends on model capability.

---

# Experiment Design

## Task

We use Python bug repair as the experimental task. Each problem consists of a buggy Python function drawn from HumanEvalPack (Muennighoff et al., 2023), a curated dataset of 164 programming problems with hand-crafted buggy solutions and unit test suites. Bug types include missing logic, operator misuse, variable misuse, excess logic, and function misuse — categories that require localized edits rather than full rewrites, ensuring that a capable agent can plausibly succeed within a bounded number of tool-use turns.

We selected Python because it is the primary training language for all models tested and because the HumanEvalPack test suite provides a deterministic pass/fail oracle with no ambiguity about correctness.

## Agent Setup

We used Claude Code (Anthropic, 2024) as the agent framework in headless mode (`claude -p`), with Bash, Read, and Edit tools enabled. The agent receives a natural-language task description pointing to a file path, runs the test suite, reads the code, applies fixes, and confirms by re-running the tests. All tool calls and intermediate reasoning are handled internally by the agent loop; we observe only the final solve status and the total number of tool-use turns reported by the session.

Two model variants were tested:

- **Sonnet** (claude-sonnet-4-6): n = 100 trials per group, across two independent replication runs of 50 problems each.
- **Opus** (claude-opus-4-7): n = 50 trials per group, one run.

Problems were drawn from the first 50 entries of the HumanEvalPack Python split (indices 0–49) and held constant across all groups and both models.

## Experimental Groups

All groups received the same task prompt:

> *"The function `[entry_point]` in `[path]/solution.py` has a bug. Run `python test_runner.py` to see the test results. Fix the bug in `solution.py` so all tests pass. When done, run the tests one final time to confirm."*

Groups differed only in what preceded this prompt:

- **Group A (control):** no prefix — the task prompt above, verbatim.
- **Group B (time + attempt):** prefix `[session_elapsed: {Xs} | attempt: 1/5]` plus a system prompt addition instructing the agent to use elapsed time to adapt its strategy if stuck.
- **Group C (attempt only):** prefix `[attempt: 1/5]` plus a system prompt addition instructing the agent to try a different approach if previous attempts failed. No elapsed time.
- **Group D (instruction only, post-hoc):** no prefix and no temporal signal, with a distinct system prompt: *"You are a debugging assistant. As you work, if you're not making progress, try a fundamentally different approach."* Note that this instruction differs from Group B (which mentions temporal signals explicitly) and from Group C (which primes the model to expect attempt count). Group D tests whether any instruction framing — without any temporal signal — produces the Group C efficiency gain. Group D was run on Sonnet only (n=50).

The elapsed time in Group B was measured from session initialization to the moment the prompt was issued (typically 0–2 seconds for the first attempt, as each trial was a fresh session). The denominator `5` was fixed across all trials.

## Exact Prompts

**Group A** — no system prompt addition. Task prompt only (see above).

**Group B system prompt:**
> "You are a debugging assistant. As you work, you will be told how much time has elapsed and how many attempts you've made. Use this information to adapt your debugging strategy — if you've been working a long time without success, try a fundamentally different approach."

**Group C system prompt:**
> "You are a debugging assistant. You will be told how many attempts you've made. If previous attempts failed, try a different approach."

**Group D system prompt:**
> "You are a debugging assistant. As you work, if you're not making progress, try a fundamentally different approach."

**Task prompt (all groups):**
> "The function `[entry_point]` in `[path]/solution.py` has a bug. Run `python test_runner.py` to see the test results. Fix the bug in `solution.py` so all tests pass. When done, run the tests one final time to confirm."

**Prompt prefix by group:**
- Group A: no prefix
- Group B: `[session_elapsed: {X}s | attempt: 1/5]`
- Group C: `[attempt: 1/5]`
- Group D: no prefix

Each trial was run as a single Claude Code session. The agent was not interrupted; it ran until it either confirmed all tests passed or exhausted its internal reasoning budget.

## Dependent Variables

**Solve rate:** whether the final state of `solution.py` passed all unit tests, evaluated by executing the test suite in a subprocess after the session ended. This provides an independent verification that does not rely on the agent's self-report.

**Tool-use turns:** the `num_turns` field returned by the Claude Code session JSON output. We verified via stream-JSON inspection that `num_turns` counts the number of times the Claude API is invoked within a session — specifically, 1 (initial call) plus 1 per tool result returned to the model. Each tool result triggers a new API call in which the model decides its next action. Multiple tool calls batched in a single model response count as one turn (until their results are returned). This means `num_turns` is a direct proxy for API call count, which maps linearly to cost and latency. It does not count internal reasoning tokens or chain-of-thought steps; it counts discrete action-planning cycles. This is our primary efficiency metric.

## Statistical Analysis

Solve rate differences were tested with Fisher's exact test (two-tailed). Tool-use turn distributions were tested with the Mann-Whitney U test (two-tailed), which makes no distributional assumptions. Effect sizes are reported as Cohen's d for turns and odds ratio for solve rate. The significance threshold is α = 0.05. No corrections for multiple comparisons were applied. The comparison structure (A vs. B, A vs. C, A vs. D per model) was specified before data collection for Groups A–C; Group D was added post-hoc. All findings should be interpreted as exploratory pending pre-registration and replication.

## Controls and Potential Confounds

**Problem difficulty:** all groups received the same 50 problems in the same order, eliminating difficulty as a between-group confound.

**Bug type distribution:** HumanEvalPack's bug types (operator misuse, missing logic, variable misuse, excess logic, function misuse) are distributed approximately uniformly across the 50 problems. Turns by bug type are consistent across groups with no single type driving the group differences (see Turns by Bug Type subsection in Results).

**Session isolation:** each trial was a fresh Claude Code session with no memory of prior trials. Rate limiting between calls was enforced with a fixed inter-trial delay (8s for Sonnet, 30s for Opus) to prevent API throttling from confounding timing measurements.

**Model version:** a single model checkpoint was used for all trials within each model tier. No fine-tuning or prompt caching was applied.

**Unblinded groups:** Claude Code's system prompt is visible to the model. Groups B and C include a system prompt addition that is absent in Group A, creating a minor confound between the temporal signal and the presence of any additional instruction. Group D was added post-hoc to decompose this confound: it carries the instruction without the count signal, allowing a clean test of whether the instruction framing alone produces the Group C effect.

---

# Results

## Solve Rate

Solve rate was identical across all groups and both models. For Sonnet, Groups A–C resolved 98–100% of problems (Group A: 100/100; Group B: 99/100; Group C: 99/100); Group D (post-hoc ablation, n=50) resolved 98% (49/50). For Opus, all three main groups resolved 100% of problems (50/50 each). Fisher's exact tests revealed no significant differences between any pair of groups for either model (all p > 0.5). Injecting temporal signals — whether elapsed time, attempt count, or both — had no measurable effect on whether the agent ultimately solved the problem.

## Tool-Use Turns

The effect on tool-use turns diverged sharply across model tiers.

**Sonnet.** Group C (attempt count only) used significantly fewer turns than the control (Group A): mean 6.49 vs. 7.10, Mann-Whitney U = 1530, p = 0.0035, Cohen d = 0.45. Group B (time + attempt count) did not differ significantly from control: mean 7.02 vs. 7.10, U = 1348, p = 0.52, d = 0.05. The difference between Group B and Group C was significant (p = 0.039, d = 0.35), with Group C being the more efficient condition. Group D (instruction only, no temporal signal; n = 50) did not differ significantly from the control: mean 6.74 vs. 7.10, p = 0.29, d = 0.27, Δ = +0.25 turns relative to Group C.

| Group | Condition | n | Mean turns | SD | vs. A (p) | d |
|-------|-----------|---|-----------|-----|-----------|---|
| A | Control | 100 | 7.10 | 1.35 | — | — |
| B | Time + count + instruction | 100 | 7.02 | 1.64 | 0.52 ns | 0.05 |
| C | Count + instruction | 100 | 6.49 | 1.37 | 0.003 ** | 0.45 |
| D | Instruction only, no signal | 50 | 6.74 | 1.32 | 0.29 ns | 0.27 |

*Table 1. Sonnet results. Groups A–C: n = 100/group, runs 1+2 pooled. Group D: n = 50, post-hoc instruction ablation.*

![Tool-use turns distribution — Sonnet vs Opus](../../figures/fig1_turns_violin.png)

*Figure 1. Distribution of tool-use turns per group for Sonnet (left) and Opus (right). White dots indicate means. Significance brackets show Mann-Whitney U tests (** p<0.01, * p<0.05).*

**Opus.** The pattern reversed. Group B (time + attempt count) used significantly more turns than control: mean 8.26 vs. 7.62, U = 912, p = 0.012, d = 0.44. Group C (attempt only) trended in the same direction but did not reach significance: mean 8.14 vs. 7.62, p = 0.097, d = 0.36. Group B and Group C did not differ from each other (p = 0.49).

| Group | Condition | Mean turns | SD | vs. A (p) | d |
|-------|-----------|-----------|-----|-----------|---|
| A | Control | 7.62 | 1.70 | — | — |
| B | Time + attempt | 8.26 | 1.16 | 0.012 * | 0.44 |
| C | Attempt only | 8.14 | 1.17 | 0.097 ns | 0.36 |

*Table 2. Opus results (n = 50/group).*

![Mean turns by group and model](../../figures/fig2_means_bar.png)

*Figure 2. Mean tool-use turns ± SEM by group and model. Error bars show standard error of the mean.*

![Direction of effect by model tier](../../figures/fig3_direction.png)

*Figure 3. Delta turns vs. control by condition and model. Negative = fewer turns than control. The effect direction reverses between Sonnet and Opus. (** p<0.01, * p<0.05, ns = not significant)*

## Replication Consistency

For Sonnet, runs 1 and 2 produced consistent means across all groups: Group A mean 7.08 (run 1) vs. 7.12 (run 2); Group B 6.90 vs. 7.14; Group C 6.28 vs. 6.70. The maximum inter-run delta was 0.42 turns (Group C), within one standard deviation. The directional pattern — C < A — was present in both runs independently.

## Instruction Ablation (Group D)

Group D was run after the initial paper draft to isolate whether the Group C effect is attributable to the instruction framing or to the count signal `[attempt: 1/5]`. Group D carried an instruction-only system prompt — *"You are a debugging assistant. As you work, if you're not making progress, try a fundamentally different approach"* — with no prefix token and no temporal signal. This instruction differs from Group B (which mentions temporal signals explicitly) and from Group C (which primes the model to expect attempt count).

Group D (Sonnet, n = 50) produced a mean of 6.74 turns (SD = 1.32), which did not differ significantly from the control: p = 0.29 (ns), Cohen d = 0.27. This places Group D squarely between Groups A and C, and numerically above Group C by 0.25 turns (D vs. C: p = 0.15 ns). The instruction alone does not replicate the Group C reduction. The count signal `[attempt: 1/5]` is the active ingredient.

This result closes the main confound identified in the original design. The presence of an additional instruction in Group B and Group C was a potential alternative explanation for the Group C effect — if the model simply responds to any additional framing by behaving differently, Group C's advantage might not be due to the count signal per se. Group D rules this out: the instruction framing without the count signal produces no significant reduction.

## Turns by Bug Type

Across both models and all groups, problems classified as "excess logic" required the most turns on average (Sonnet Group A: 9.0; Opus Group A: 9.4), while "function misuse" and "variable misuse" required the fewest (Sonnet Group A: 6.0–7.0). The treatment effects were consistent in direction across bug types, with no single bug type driving the group differences.

---

# Discussion

## Why Attempt Count Helps Sonnet

The efficiency gain in Sonnet's Group C is consistent with the metareasoning gap identified by Sumers et al. (2023): agents without a budget signal allocate tool-use turns as if each attempt were the first. When the agent knows it is on attempt 1 of 5, it has a concrete stopping criterion that is absent in the control condition. Rather than exploring multiple diagnostic hypotheses in sequence — reading the code, running the tests, forming a theory, applying a fix, re-reading if it fails — the agent appears to converge on a fix earlier, accepting higher uncertainty in its hypothesis and committing to an edit sooner.

This is consistent with Self-Refine's diminishing-returns curve (Madaan et al., 2023): the largest gain from iteration occurs at step 1→2, because that is when the agent's uncertainty is highest. An attempt count signal short-circuits unnecessary early-turn exploration by signaling that the current attempt is one of several available — a form of Bayesian updating on available resources.

Critically, the effect is on *efficiency* (turns), not *accuracy* (solve rate). The agent does not solve more problems — it solves them with less effort. This rules out the hypothesis that attempt count provides task-relevant information. Instead, it provides a resource signal that calibrates planning depth.

## Why Elapsed Time Does Not Help — And May Add Noise

For Sonnet, Group B (time + attempt) performed no better than the control despite including the same attempt count as Group C. The most parsimonious explanation is interference: the elapsed time signal adds context that the model must process, and that processing consumes reasoning capacity that would otherwise go toward the debugging task. The model attends to the time value, attempts to interpret its significance, and produces a slightly noisier action plan — canceling the benefit of the count signal.

An important design caveat: in this experiment, elapsed time was necessarily near-zero for all Group B trials (typically 0–2 seconds), since each trial began as a fresh session with no prior history. The model received a signal such as `[session_elapsed: 1s | attempt: 1/5]` — a value informationally empty of any signal about task difficulty or progress. This means we cannot determine from this experiment whether elapsed time would function differently in long-horizon sessions where the value is non-trivial (e.g., 3 hours into a complex bug). The finding that elapsed time provides no benefit is valid for the near-zero regime tested here; it should not be generalized to all possible elapsed-time values without further study.

This is consistent with the temporal reasoning literature. LoCoMo (Maharana et al., 2024) shows that LLMs underperform on elapsed-time questions by 73 percentage points relative to humans. Alonso et al. (2024) find that semantic retrieval over timestamps achieves 3–6% recall, while ordinal session-number retrieval achieves 90%. If the model cannot reliably reason about elapsed time in comprehension tasks, it is unlikely to use it productively as a planning signal in an action loop. The time value becomes noise rather than signal.

**Group D rules out the instruction-framing alternative.** A potential objection to the Group C finding is that its advantage over the control stems not from the count signal but from the presence of any additional instruction — a general priming effect from being told to try a different approach. Group D (Sonnet, n = 50) tests this directly: it delivers the same instruction as Group B but without any prefix token or temporal signal. Group D did not differ significantly from the control (p = 0.29, d = 0.27), and its mean of 6.74 turns sits 0.25 turns above Group C. The instruction alone does not produce the effect. The count signal `[attempt: 1/5]` is the causally active element. This also refines the mechanistic account: Group C's instruction may prime the model to expect a structured resource budget, making the count signal more legible — but the instruction without the signal is inert. The signal and the framing work together, with the signal as the necessary condition.

## Why Opus Responds Differently

The reversal in Opus — where temporal signals *increase* tool-use turns — suggests a different mechanism. To be precise about what "reversal" means here: it is Group C (count only) that reaches significance for Sonnet (p=0.003), while it is Group B (elapsed time + count) that reaches significance for Opus (p=0.012). These are not the identical signal reversing direction — different conditions reached significance in each model tier, with Group C trending in the same direction as Group B for Opus (p=0.097) but not reaching significance with n=50. Opus, as a more capable model, may treat the attempt-count or time signal not as a resource constraint but as an invitation to be more thorough. Where Sonnet reads "attempt 1/5" as *commit sooner*, Opus may read it as *you have 4 more tries if this one fails, so explore now*.

This is a form of the explore-exploit tradeoff applied to debugging. A more capable model with a higher baseline confidence in its reasoning may rationally allocate more turns to exploration when it knows retries are available — the opposite of what a less confident model does. The result is more turns per trial, but with identical solve rate, suggesting the extra turns are spent on verification and hypothesis enumeration rather than on finding the fix itself.

This interpretation is speculative; we cannot observe the agent's internal reasoning directly. But it is consistent with Opus's higher baseline turn count (7.62 vs. Sonnet's 7.10 in the control) and with the literature on capability-dependent self-refinement: Madaan et al. (2023) note that weaker models cannot reliably detect their own failures, and their self-feedback adds noise rather than signal. The inverse may hold for frontier models: stronger models detect success earlier and use additional context to explore more thoroughly before committing.

## Mechanistic Evidence (Preliminary)

To probe whether Group C's efficiency gain reflects explicit use of the count signal or implicit anchoring, we captured the full visible reasoning text from 15 sessions per group (A, C, D) using Claude Code's stream-JSON output. We coded each session for explicit mentions of the attempt signal (words matching: "attempt", "tries", "remaining", "N of M") and for strategy-change language ("different approach", "alternatively", "try instead").

In 14 of 15 Group C sessions (93%), the model never verbalized the attempt count. For comparison, Group A (control, no signal) showed 0% signal verbalization — as expected, since no signal was provided. Group D (instruction only) also showed 0% verbalization. The meaningful comparison is reasoning length and strategy-word frequency, where the gradient A (754 chars, 0.60 strategy words) > D (684 chars, 0.47) > C (602 chars, 0.33) holds consistently. Reasoning text length was 20% shorter in Group C than control (602 vs. 754 characters on average), and strategy-change language was less frequent (0.33 vs. 0.60 instances per session). Group D (instruction only) fell between the two: reasoning length 684 characters, strategy mentions 0.47 per session — more compressed than control but less so than Group C.

The gradient A > D > C on both reasoning length and strategy mentions mirrors the turn-count gradient, and holds without any explicit verbalization of the signal. This pattern is consistent with **anchoring rather than explicit metareasoning**: the `[attempt: 1/5]` token appears to compress the model's planning horizon implicitly, without the model consciously thinking "I have four more tries." The instruction in Group D achieves a partial compression effect, but the structured count signal in Group C achieves a larger one — without any explicit deliberation about the constraint.

We note two important caveats. First, n=15 per group is insufficient for strong causal claims; the reasoning-length difference (A vs. C: −152 chars) is descriptive, not statistically tested at this sample size. Second, reasoning text length is a proxy for planning depth, not a direct measure of cognitive process. The anchoring interpretation is the most parsimonious account consistent with the data, but mechanistic studies using activation analysis or attribution methods would be needed to confirm it.

## Practical Implications

Three recommendations follow from these results for practitioners building LLM agent systems:

**1. Inject attempt count, not elapsed time.** Attempt count is a three-token addition to the prompt (`[attempt: N/M]`) with no computational cost. For mid-tier models, it reduces tool-use turns — and by extension, API costs and latency — without affecting task success. Elapsed time provides no benefit and may introduce noise.

**2. Calibrate by model tier.** The effect direction reverses between Sonnet and Opus. For Sonnet, count signals reduce turns (p=0.003). For Opus, the full signal (Group B) increases turns (p=0.012), while count-only (Group C) trends similarly but does not reach significance with n=50. A system prompt optimized for efficiency with Sonnet may increase turn count with Opus. Validate per-model before deployment. Agent harness designers should treat temporal signal configuration as a model-specific hyperparameter, not a universal default.

**3. Solve rate is not the right metric for efficiency studies.** All conditions converged to the same solve rate, but tool-use turns varied by up to 10% between groups. Cost and latency optimization in deployed agents requires measuring turns or token counts directly, not just pass/fail outcomes.

---

# Limitations

**Single provider.** Both models tested are from the same provider (Anthropic). The effect may not generalize to GPT-4o, Gemini, or open-source models such as Llama 3 or Mistral. The capability-moderation finding — that the effect direction reverses between model tiers — requires replication with models from different providers and training pipelines before it can be claimed as a general principle.

**Unequal sample sizes.** Sonnet was tested with n=100 per group across two independent runs; Opus with n=50 in a single run. The Opus results are less statistically powered, and the Group C trend (p=0.097) falls below the significance threshold. A fully powered Opus replication would require approximately 100 trials per group to match Sonnet's precision. The most prominent finding — that temporal signals increase turns for Opus while decreasing them for Sonnet — rests on a single run with n=50 for Opus. This is the least statistically robust result in the paper, and the direction reversal should be treated as preliminary until replicated with n=100 across two independent runs.

**Instruction–signal interaction.** The post-hoc Group D ablation (Sonnet, n = 50) confirms that the instruction framing alone does not replicate the Group C reduction (p = 0.29 ns, d = 0.27), establishing the count signal as the necessary active ingredient. However, Group D's mean (6.74 turns) falls between the control (7.10) and Group C (6.49), leaving open the possibility that the instruction contributes a partial, non-significant nudge that amplifies the count signal's effect in Group C. In other words, the instruction may prime the model to treat `[attempt: 1/5]` as a meaningful resource boundary rather than decorative text — making the full Group C condition more than the sum of its parts. This interaction is not yet decomposed at the level of mechanistic evidence; it remains a plausible account consistent with the observed effect sizes.

**Fixed denominator and static numerator.** The prefix `[attempt: 1/5]` is identical across all trials: the numerator is always 1 (each trial is a fresh session) and the denominator 5 was set arbitrarily. We cannot distinguish whether the effect is driven by the ordinal signal ("this is attempt 1, implying more are available"), the total budget implied by the denominator ("there are 5 attempts"), or the N/M structure itself. Future work should vary the denominator and, in multi-turn sessions, advance the numerator across retries to test whether the signal gains potency as attempts accumulate.

**Benchmark scope.** HumanEvalPack bugs are synthetic, small (typically 5–30 lines), and drawn from a well-known dataset likely present in the models' training data. Real-world debugging tasks involve larger codebases, ambiguous specifications, and bugs that require multi-file reasoning. Whether the attempt-count effect scales to harder, longer tasks is unknown.

**Unobservable mechanism.** Our interpretation of *why* attempt count affects Opus and Sonnet differently is based on aggregate turn counts. We cannot observe the agent's internal reasoning, confirm that it attended to the temporal signal, or verify that the extra turns in Opus correspond to exploration rather than confusion. Mechanistic studies using chain-of-thought traces or activation analysis would be needed to validate the proposed explanation.

---

# Conclusion

We asked whether injecting temporal signals into an LLM agent's context changes debugging efficiency, and whether the answer depends on model capability. The results are clear on both counts. Solve rate is unaffected by any temporal signal across both model tiers. Tool-use efficiency, however, diverges sharply: count-only signal (Group C) reduces turns for Sonnet (p=0.003, d=0.45); the full temporal signal (Group B: elapsed time + count) increases turns for Opus (p=0.012, d=0.44), with Group C trending similarly for Opus but not reaching significance (p=0.097). Elapsed time adds no benefit for Sonnet and may introduce noise.

The practical takeaway is simple. Inject attempt count — not elapsed time — into your agent's prompt. It is a three-token addition with no computational cost. Expect efficiency gains for mid-tier models and more exploratory behavior for frontier models. Treat it as a model-specific hyperparameter, not a universal default. And measure tool-use turns, not just solve rate, when evaluating agent efficiency. The gap between what agents accomplish and how efficiently they accomplish it is where the cost of deployment lives.

---

# References

Alonso, N., Figliolia, T., Ndirango, A., & Millidge, B. (2024). Toward conversational agents with context and time sensitive long-term memory. *arXiv preprint arXiv:2406.00057*.

Han, T., Wang, Z., Fang, C., Zhao, S., Ma, S., & Chen, Z. (2024). Token-budget-aware LLM reasoning. *arXiv preprint arXiv:2412.18547*.

Jang, J., Boo, M., & Kim, H. (2023). Conversation chronicles: Towards diverse temporal and relational dynamics in multi-session conversations. *arXiv preprint arXiv:2310.13420*.

Maharana, A., Lee, D.-H., Tulyakov, S., Bansal, M., Barbieri, F., & Fang, Y. (2024). Evaluating very long-term conversational memory of LLM agents. *arXiv preprint arXiv:2402.17753*.

Madaan, A., Tandon, N., Gupta, P., Hallinan, S., Gao, L., Wiegreffe, S., … & Clark, P. (2023). Self-refine: Iterative refinement with self-feedback. *Advances in Neural Information Processing Systems, 36*.

Muennighoff, N., Liu, Q., Zebaze, A., Zheng, Q., Hui, B., Zhuo, T. Y., … & Shi, L. (2023). OctoPack: Instruction tuning code large language models. *arXiv preprint arXiv:2308.07124*.

NousResearch. (2025). Feature: Iteration budget pressure — warn the LLM before max iterations hit [GitHub Issue #414]. *hermes-agent repository*. https://github.com/NousResearch/hermes-agent/issues/414

Packer, C., Wooders, S., Lin, K., Fang, V., Patil, S. G., Stoica, I., & Gonzalez, J. E. (2023). MemGPT: Towards LLMs as operating systems. *arXiv preprint arXiv:2310.08560*.

Pink, M., Wu, Q., Vo, V. A., Turek, J., Mu, J., Huth, A., & Toneva, M. (2025). Position: Episodic memory is the missing piece for long-term LLM agents. *arXiv preprint arXiv:2502.06975*.

Rorseth, J., Faisal, A., Sinha, M., & Nakayama, K. (2025). TraceCoder: A trace-driven multi-agent framework for automated debugging of LLM-generated code. *arXiv preprint arXiv:2602.06875*.

Sumers, T. R., Yao, S., Narasimhan, K., & Griffiths, T. L. (2023). Cognitive architectures for language agents. *arXiv preprint arXiv:2309.02427*.

Yang, W., Li, Y., Fang, M., & Chen, L. (2024). Enhancing temporal sensitivity and reasoning for time-sensitive question answering. *arXiv preprint arXiv:2409.16909*.

---

