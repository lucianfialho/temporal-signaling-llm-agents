---
arxiv: 2303.17651
title: "Self-Refine: Iterative Refinement with Self-Feedback"
authors: Madaan et al.
year: 2023
tags: [iterative-refinement, self-feedback, prompting, llm-agents, tool-use-reduction]
relevance: high
---

## One-line summary
A single LLM iteratively critiques and rewrites its own output using natural-language feedback, improving quality by ~20% on average across 7 tasks without any additional training.

## What they did
Self-Refine is a three-step loop applied at inference time: (1) generate an initial output, (2) prompt the same model to produce specific, actionable feedback on that output, (3) prompt the model again to refine the output using that feedback. Steps 2 and 3 repeat until a stopping criterion is met or a maximum iteration count (4) is reached. No gradient updates, reward models, or human annotations are required — only few-shot prompt engineering.

The method was evaluated across seven tasks spanning natural language (dialogue response generation, sentiment reversal, acronym generation, constrained generation) and code (code optimization, code readability improvement) plus math reasoning. The backbone models were GPT-3.5 (text-davinci-003), ChatGPT (gpt-3.5-turbo), and GPT-4; code tasks also used Codex. The stopping condition is task-specific — for some tasks the model emits a scalar quality score per aspect, and iteration halts when no aspect still needs improvement.

The feedback prompt is the critical design choice. The authors distinguish *specific, actionable feedback* (e.g., "this loop is O(n^6); replace it with dynamic programming") from *generic feedback* (e.g., "improve efficiency") and from *no feedback* at all. Ablations show that each level down degrades performance, with specific feedback being strictly necessary for tasks like Sentiment Reversal, which fails entirely without it.

## Key findings
- Self-Refine consistently outperforms single-pass generation across all 7 tasks and all 3 backbone LLMs, with absolute improvements of 5–49%.
- Largest gains in preference-based tasks: Dialogue Response Generation improves 49.2 pp for GPT-4 (25.4 → 74.6%); Constrained Generation improves 30 pp.
- Diminishing returns with iterations: most gain occurs at iteration 1→2; by iteration 3 marginal improvement is small but still positive.
- Math Reasoning is the weakest domain (~0 gain), because the model's self-feedback incorrectly reports "everything looks good" 94% of the time even when the answer is wrong; gains appear only when an external oracle flags errors.
- Self-Refine beats generating k=4 independent samples and picking the best: the refined output is preferred by humans over all 4 independent draws.
- Weaker models (Vicuna-13B) fail: they cannot reliably produce feedback in the required format, and even given oracle feedback they ignore refinement instructions.
- Failure analysis: 94% of failures trace to bad feedback (wrong localization 33%, wrong fix suggestion 61%), not to the refiner misapplying good feedback (6%).

## Relevance to our experiment
Self-Refine is the closest structural analogue to the mechanism we are studying. In our experiment the agent accumulates attempt-count information across debugging turns; Self-Refine shows that iterative self-feedback — a proxy for accumulated attempt count — does reduce the number of "effective" problem-solving steps needed by guiding the model away from already-tried dead ends. Crucially, the paper demonstrates that *attempt count matters*: early iterations produce the largest gains, and later iterations add less value, matching the hypothesis that the agent "uses up" its uncertainty about what to try with each attempt. The code-optimization results are directly applicable to debugging tasks.

The paper also provides a critical null result: math reasoning (a domain with unambiguous correctness) barely benefits from self-feedback. This supports our hypothesis that the mechanism works not through elapsed time but through the qualitative information encoded in each attempt — the model must be able to perceive whether an attempt succeeded or failed.

## Gaps / what they didn't do
- No measurement of *tool-use turns*: Self-Refine counts refinement iterations as a proxy for effort, but never measures API calls, search queries, or tool invocations per task — exactly the dependent variable in our experiment.
- Elapsed time is not tracked at all; time is not a variable in their framework, only discrete iteration count.
- All tasks are well-specified; no study of how attempt-count signals behave when the stopping criterion is ambiguous or external feedback is unavailable (the math failure mode exposes this but is not studied systematically).
- Weaker open-source models are only briefly examined (Vicuna-13B); the regime where self-feedback helps is not characterized as a function of model capability.
- No multi-agent setup: a single LLM acts as generator, critic, and refiner simultaneously, so cross-agent coordination and memory across sessions are not studied.

## Key quotes
> "Like humans, large language models (LLMs) do not always generate the best output on their first try. [...] \[Self-Refine\] does not require any supervised training data, additional training, or reinforcement learning, and instead uses a single LLM as the generator, refiner and the feedback provider."

> "Figure 4 highlights the diminishing returns in the improvement as the number of iterations increases. Overall, having multiple feedback-refine iterations significantly enhances the quality of the output, although the marginal improvement naturally decreases with more iterations."

## Citation
Madaan, A., Tandon, N., Gupta, P., Hallinan, S., Gao, L., Wiegreffe, S., Alon, U., Dziri, N., Prabhumoye, S., Yang, Y., Gupta, S., Majumder, B. P., Hermann, K., Welleck, S., Yazdanbakhsh, A., & Clark, P. (2023). Self-Refine: Iterative Refinement with Self-Feedback. *arXiv preprint arXiv:2303.17651*.
