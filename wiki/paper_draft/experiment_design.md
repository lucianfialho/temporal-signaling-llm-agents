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
- **Group D (instruction only, post-hoc):** no prefix and no temporal signal, but the same system prompt addition as Group B: *"You are a debugging assistant. As you work, if you're not making progress, try a fundamentally different approach."* Group D was added after the initial draft to address the instruction confound in Group B: if the Group C effect were driven by the instruction framing rather than the count signal, Group D should replicate it. Group D was run on Sonnet only (n=50).

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
