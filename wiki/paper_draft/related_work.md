# Related Work

Our experiment sits at the intersection of three research streams that have not previously been connected: iterative refinement in LLM agents, temporal reasoning in language models, and memory architecture for long-horizon agents.

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

## Gap Addressed by This Work

None of the prior work directly manipulates temporal signals as independent variables in a tool-using agent setting with a pass/fail oracle. Self-Refine does not track elapsed time or attempt count as a context variable. CoALA identifies metareasoning as a gap but offers no empirical test. The temporal reasoning and memory papers study retrieval quality and comprehension, not downstream agent behavior in an action loop. Our experiment is the first to isolate elapsed time vs. attempt count in a controlled, agentic debugging task — and the first to show that the effect direction depends on model capability.
