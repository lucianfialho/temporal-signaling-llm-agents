---
arxiv: 2310.08560
title: "MemGPT: Towards LLMs as Operating Systems"
authors: Packer et al.
year: 2023
tags: [memory-management, long-context, agent-architecture, function-calling, temporal-state]
relevance: medium
---

## One-line summary
MemGPT gives an LLM OS-style hierarchical memory — main context (RAM) and external storage (disk) — letting it self-direct paging via function calls to operate over unbounded context lengths.

## What they did
MemGPT treats the LLM's fixed context window as "physical memory" and introduces two external tiers: *recall storage* (a searchable message database) and *archival storage* (an arbitrary-length vector-searchable document database). The LLM controls what is in context at any moment by calling MemGPT's read/write functions, analogous to how an OS manages virtual memory paging. The LLM processor takes concatenated prompt tokens as input and emits either a user-facing response (a *yield*) or a function call with `request_heartbeat=true`, which chains directly into the next LLM inference without user interaction.

The main-context prompt is divided into three fixed sections: (1) read-only system instructions describing the memory architecture and function schemas, (2) a read/write *working context* block for persistent key facts (persona, user preferences), and (3) a FIFO queue holding recent messages. When the queue nears the token limit, MemGPT receives an automatic memory-pressure warning and is expected to use functions to flush important content to working context or archival storage before the queue manager evicts the oldest messages and writes a recursive summary.

MemGPT was evaluated on two domains: (a) *multi-session conversational agents*, using an expanded Multi-Session Chat (MSC) dataset with a new Deep Memory Retrieval (DMR) task and a conversation-opener engagement task; and (b) *document analysis*, using a retriever-reader QA benchmark and a novel nested key-value retrieval task requiring multi-hop lookups across UUIDs stored in archival memory. Baselines used fixed-context GPT models with recursive summarization of past sessions. MemGPT ran on top of GPT-3.5 Turbo, GPT-4, and GPT-4 Turbo.

## Key findings
- On Deep Memory Retrieval (consistency), MemGPT+GPT-4 reaches 92.5% accuracy vs. 32.1% for baseline GPT-4 and 35.3% for GPT-4 Turbo without MemGPT.
- MemGPT conversation openers match or exceed human-written openers on persona-similarity metrics (SIM-H) with GPT-4 and GPT-4 Turbo backbones.
- On document QA, fixed-context baselines plateau at retriever accuracy; MemGPT can iteratively page through archival results, decoupling performance from retriever top-K constraint.
- Nested KV retrieval: fixed-context GPT-4 hits 0% accuracy at 3 nesting levels; MemGPT+GPT-4 maintains accuracy across all tested nesting depths by chaining function calls.
- GPT-3.5 Turbo is substantially weaker as a MemGPT backbone due to limited function-calling reliability; results confirm that the orchestration mechanism demands strong instruction-following.
- Function chaining (`request_heartbeat=true`) is the core mechanism enabling multi-step retrieval within a single user turn — effectively compressing what would be many sequential tool-use turns into one logical action sequence.

## Relevance to our experiment
MemGPT is relevant as a concrete architecture for agents that manage their own state across turns. Its memory-pressure warnings and recursive summarization are mechanisms that make the agent explicitly aware of *how many interactions have occurred* (via the FIFO queue length and the recursive summary). This is a structural analogue to "attempt count" signaling: the queue depth is a proxy for session age, and the recursive summary encodes which approaches have already been tried.

The nested KV task directly models multi-hop debugging: each lookup (attempt) produces either a terminal answer or a new search key. MemGPT's success there — sustained through many nesting levels by function chaining — suggests that architectures that track attempt history in working context outperform those that let history scroll out of the window. This supports our hypothesis that attempt-count information (not mere elapsed time) is the operative signal.

## Gaps / what they didn't do
- No measurement of attempt count as an independent variable; the paper does not isolate whether it is the *number* of prior retrievals or the *semantic content* of prior failures that drives improvement.
- Elapsed time is completely absent as a variable; all evaluations are turn-based, not time-based — consistent with our hypothesis but never tested against it.
- Debugging tasks are not studied; the domains are conversation and document QA, both of which have clear external ground truth. The debugging scenario (where failure signals are ambiguous and incremental) is not addressed.
- The recursive summary mechanism compresses attempt history lossy; it is unknown how much useful "what I already tried" information survives eviction, which is directly relevant to whether attempt count signals degrade with session length.
- No ablation isolating the contribution of working-context persistence of prior attempt outcomes vs. raw retrieval depth.

## Key quotes
> "Using function calls, LLM agents can read and write to external data sources, modify their own context, and choose when to return responses to the user. These capabilities allow LLMs to effectively 'page' in and out information between context windows (analogous to 'main memory' in operating systems) and external storage."

> "Awareness of context limits is a key aspect in making the self-editing mechanism work effectively; to this end MemGPT prompts the processor with warnings regarding token limitations to guide its memory management decisions."

## Citation
Packer, C., Wooders, S., Lin, K., Fang, V., Patil, S. G., Stoica, I., & Gonzalez, J. E. (2023). MemGPT: Towards LLMs as Operating Systems. *arXiv preprint arXiv:2310.08560*. In *Proceedings of the 41st International Conference on Machine Learning (ICML)*.
