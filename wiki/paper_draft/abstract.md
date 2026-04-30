# Abstract

LLM agents in iterative loops have no built-in sense of how many attempts they have made. We ask whether injecting this information changes debugging efficiency — and whether the effect depends on model capability.

We ran a controlled experiment on HumanEvalPack Python bugs using Claude Code as the agent, testing four conditions: no temporal signal (control, Group A), elapsed time + attempt count (Group B), attempt count alone (Group C), and instruction framing without any signal (Group D, ablation). We replicated across two model tiers: Sonnet (n=100/group, two independent runs) and Opus (n=50/group, one run).

Solve rate was identical across all groups (~98–100%). For Sonnet, Group C used significantly fewer tool-use turns than control (p=0.003, Cohen d=0.45); Group D (instruction without signal) did not (p=0.29 ns), establishing the count signal as the causally active element. For Opus, Group B used significantly more turns than control (p=0.012, d=0.44), with Group C trending similarly (p=0.097).

A chain-of-thought analysis (n=15/group) found that 93% of Group C sessions never verbalized the attempt count, yet produced 20% shorter reasoning text — consistent with implicit anchoring rather than explicit metareasoning.

We conclude that attempt count is a low-cost signal with model-dependent effects: it induces efficiency in mid-tier models, apparently through anchoring, while frontier models show increased exploratory behavior under the full temporal signal (Group B). To our knowledge, this is the first controlled study isolating elapsed time vs. attempt count as agent planning signals, and the first to show that the effect direction depends on model capability.
