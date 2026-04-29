---
arxiv: 2309.02427
title: "Cognitive Architectures for Language Agents"
authors: Sumers et al.
year: 2023
tags: [language-agents, cognitive-architecture, memory, decision-making, action-space, planning]
relevance: high
---

## One-line summary
CoALA proposes a unified framework for language agents organized around three axes: memory modules (working, episodic, semantic, procedural), a structured action space (internal: reasoning/retrieval/learning; external: grounding), and a decision cycle of plan-then-execute.

## What they did
Drew on cognitive science (Soar, production systems, Newell & Simon) to propose a conceptual taxonomy for LLM-based agents. Retrospectively mapped ~20 existing agents (ReAct, Voyager, Generative Agents, Tree of Thoughts, SayCan) onto the framework. Prospectively identified underexplored design directions in memory, learning, and decision-making. No new empirical experiments — the contribution is taxonomic and architectural.

## Key findings
- Agents can be cleanly described by: what they store (memory types), what they can do (action types), and how they choose (decision procedure).
- Most existing agents only implement *proposal* in their decision cycle; propose-evaluate-select (deliberate reasoning) is largely unexplored.
- Internal actions (reasoning, retrieval, learning) are the distinguishing factor between simple LLM wrappers and cognitive agents.
- Longer context windows reduce but do not eliminate the need for explicit long-term memory.
- Metareasoning — adaptive allocation of compute to planning — is identified as a critical open problem: agents currently fix a search budget rather than deciding when planning is worth the cost.
- Safety of the action space matters: learning actions (especially procedural modification) and grounding actions (bash, physical actuators) carry different risk profiles.

## Relevance to our experiment
How this connects to: "attempt count (not elapsed time) reduces agent tool-use turns in debugging tasks"

CoALA is the most directly applicable framework for situating this finding. Specifically:

1. **Attempt count as an internal state variable in working memory.** CoALA defines working memory as the hub that persists across decision cycles. Attempt count is exactly such a variable — a counter in working memory that updates each cycle. CoALA predicts that agents using this variable in their planning stage should produce different (and potentially better-calibrated) action proposals.

2. **Elapsed time as absent from the standard action-observation loop.** CoALA's decision cycle is driven by observations from grounding actions, not by wall-clock time. Time is not naturally represented in working memory; attempt count is. This structurally explains *why* attempt count is more effective than elapsed time: it maps directly onto the agent's internal cycle count, whereas elapsed time does not.

3. **Tool-use efficiency as a decision-making outcome.** Reducing tool-use turns corresponds to the agent reaching a grounding action (submitting a fix) with fewer intermediate reasoning/retrieval cycles. Under CoALA, this is a decision-making efficiency problem — the agent's proposal-evaluate-select loop is terminating earlier, which CoALA would classify as improved metareasoning.

4. **The "size of the action space" tradeoff.** CoALA explicitly warns that larger action spaces require more complex decision-making. In debugging, the relevant actions are: (a) read file, (b) run test, (c) apply fix, (d) submit. If attempt count prunes the agent's tendency to over-explore early actions, it is effectively reducing the effective action space per cycle — consistent with CoALA's guidance to "take the minimal action space necessary."

## Gaps / what they didn't do
- No empirical experiments; all agent mappings are post-hoc and qualitative.
- Does not model *time* as a first-class variable in any memory module — temporal awareness is absent from the framework.
- Does not study attempt count or iteration count as a planning signal; metareasoning is flagged as future work but not operationalized.
- Decision cycle is treated as homogeneous across iterations; no discussion of how agent behavior should (or does) change as a function of how many cycles have elapsed.
- No treatment of debugging or iterative code repair as a task domain.
- Procedural memory modification is flagged as risky and understudied; no mechanisms proposed.

## Key quotes
> "Metareasoning to improve efficiency. LLM calls are both slow and computationally intensive. Using LLMs for decision-making entails a balance between their computational cost and the utility of the resulting improved plan. Most LLM reasoning methods fix a search budget by specifying a depth of reasoning, but humans appear to adaptively allocate computation."

> "The tradeoff of the action space vs. decision-making complexities is a basic problem to be considered before agent development, and taking the minimal action space necessary to solve a given task might be preferred."

> "CoALA structures this top-level program into decision cycles which yield an external grounding action or internal learning action. In each cycle, program code defines a sequence of reasoning and retrieval actions to propose and evaluate alternatives (planning stage), then executes the selected action (execution stage)."

> "Working memory maintains active and readily available information as symbolic variables for the current decision cycle. This includes perceptual inputs, active knowledge (generated by reasoning or retrieved from long-term memory), and other core information carried over from the previous decision cycle (e.g., agent's active goals)."

## Citation
Sumers, T. R., Yao, S., Narasimhan, K., & Griffiths, T. L. (2023). Cognitive Architectures for Language Agents. *arXiv preprint arXiv:2309.02427*.
