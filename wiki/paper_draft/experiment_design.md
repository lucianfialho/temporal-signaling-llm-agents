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
- **Group C (attempt only):** prefix `[attempt: 1/5]` with no system prompt addition and no elapsed time.

The elapsed time in Group B was measured from session initialization to the moment the prompt was issued (typically 0–2 seconds for the first attempt, as each trial was a fresh session). The denominator `5` was fixed across all trials.

Each trial was run as a single Claude Code session. The agent was not interrupted; it ran until it either confirmed all tests passed or exhausted its internal reasoning budget.

## Dependent Variables

**Solve rate:** whether the final state of `solution.py` passed all unit tests, evaluated by executing the test suite in a subprocess after the session ended. This provides an independent verification that does not rely on the agent's self-report.

**Tool-use turns:** the `num_turns` field returned by the Claude Code session JSON output. We verified via stream-JSON inspection that `num_turns` counts the number of times the Claude API is invoked within a session — specifically, 1 (initial call) plus 1 per tool result returned to the model. Each tool result triggers a new API call in which the model decides its next action. Multiple tool calls batched in a single model response count as one turn (until their results are returned). This means `num_turns` is a direct proxy for API call count, which maps linearly to cost and latency. It does not count internal reasoning tokens or chain-of-thought steps; it counts discrete action-planning cycles. This is our primary efficiency metric.

## Statistical Analysis

Solve rate differences were tested with Fisher's exact test (two-tailed). Tool-use turn distributions were tested with the Mann-Whitney U test (two-tailed), which makes no distributional assumptions. Effect sizes are reported as Cohen's d for turns and odds ratio for solve rate. The significance threshold is α = 0.05. No corrections for multiple comparisons were applied given the pre-registered comparison structure (A vs. B, A vs. C, B vs. C per model).

## Controls and Potential Confounds

**Problem difficulty:** all groups received the same 50 problems in the same order, eliminating difficulty as a between-group confound.

**Bug type distribution:** HumanEvalPack's bug types (operator misuse, missing logic, variable misuse, excess logic, function misuse) are distributed approximately uniformly across the 50 problems. We report turns by bug type in Appendix A.

**Session isolation:** each trial was a fresh Claude Code session with no memory of prior trials. Rate limiting between calls was enforced with a fixed inter-trial delay (8s for Sonnet, 30s for Opus) to prevent API throttling from confounding timing measurements.

**Model version:** a single model checkpoint was used for all trials within each model tier. No fine-tuning or prompt caching was applied.

**Unblinded groups:** Claude Code's system prompt is visible to the model. Groups B and C include a system prompt addition that is absent in Group A, creating a minor confound between the temporal signal and the presence of any additional instruction. We partially address this in the Discussion.
