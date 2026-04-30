# Introduction

LLM-based agents deployed on iterative tasks — debugging, code generation, tool use — operate without any built-in sense of how long they have been working or how many attempts they have made. Each turn in the agent loop is processed with the same context as the first. This is not a fundamental limitation of the architecture, but a design choice: the harness simply does not inject this information.

The question we ask is whether it should. Temporal context is cheap to compute and trivial to inject. If it changes agent behavior in useful ways — reducing wasted effort, triggering strategy shifts — the cost-benefit is obvious. If it does not, that too is worth knowing.

We designed a controlled experiment around this question. Using Claude Code as the agent on HumanEvalPack Python debugging problems, we compared three groups: a control with no temporal signal, a treatment with elapsed time and attempt count, and an ablation with attempt count alone. We replicated across two model tiers — Sonnet and Opus — to test whether any effect is model-dependent.

The results were unexpected. Solve rate was identical across all conditions. But the effect on tool-use turns diverged sharply by model: Sonnet became more efficient with attempt count, Opus became more exploratory with the full temporal signal. The same prompt prefix produced opposite efficiency effects depending on model capability: for Sonnet, attempt count (Group C) reduced turns; for Opus, the full signal (Group B) increased turns. The conditions that reached significance differed by model tier.

This paper makes three contributions: (1) to our knowledge, the first controlled experiment isolating elapsed time vs. attempt count as agent context signals; (2) evidence that model capability moderates the direction of the effect; (3) a practical recommendation for agent system designers — inject attempt count, and calibrate expectations by model tier.
