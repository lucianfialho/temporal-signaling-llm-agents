---
arxiv: 2406.00057
title: "Toward Conversational Agents with Context and Time Sensitive Long-term Memory"
authors: Nick Alonso et al.
year: 2024
tags: [RAG, temporal-retrieval, conversational-memory, chain-of-tables, metadata-retrieval, long-term-memory]
relevance: medium
---

## One-line summary
Standard semantic RAG completely fails time-based queries in chat logs; a hybrid chain-of-tables + semantic retrieval system achieves ~90% recall on temporal questions that pure embedding search cannot answer.

## What they did
Identified two failure modes of standard RAG in conversational settings: (1) time/event-based queries ("what did we discuss in session 5?", "what did we talk about last Tuesday?") and (2) ambiguous queries using pronouns/demonstratives without resolved referents. Built a new benchmark by extending the LoCoMo long-form dialogue dataset: added per-response timestamps, session metadata, and generated 2,134 temporal questions across 11 query types. Developed a retrieval system combining: (a) chain-of-tables (CoTable) for metadata lookup using two simple functions (f_value, f_between), (b) semantic vector search for content, (c) an LLM classifier routing each query to the right retrieval mode, and (d) an LLM query rewriter for ambiguous queries. Tested with hMistral-7b and GPT-3.5-turbo.

## Key findings
- Pure semantic retrieval recall on time-based queries: 3–6% (effectively 0 useful signal).
- CoTable + Semantic with GPT-3.5: 90% recall on time-based queries, 90% recall on time+content queries.
- Query rewriting for ambiguous queries recovers ~83–89% recall (vs ~3% on raw ambiguous queries).
- Meta-semantic classifier that routes query type is essential: without it, performance drops ~50% for hMistral on pure time queries.
- Session number ("what did we discuss in session N?") is the most reliably retrievable temporal unit.
- Timestamps simulated by assuming average human speech rate (words/minute) from Tauroza & Allison (1990).

## Relevance to our experiment
How this connects to: "attempt count (not elapsed time) reduces agent tool-use turns in debugging tasks"

Directly relevant to the retrieval/memory side of temporal agent design. The paper shows that *ordinal event identifiers* (session number, attempt number, "Nth conversation") are more tractable retrieval keys than continuous elapsed time. Their finding that `f_value(session_index, [5])` achieves high precision while semantic search fails parallels our hypothesis: the agent's internal representation of "attempt N" (a discrete count) may be a more actionable signal than elapsed wall-clock time. Also relevant: their classifier correctly identifies when a query is metadata-referential vs. content-referential — analogous to our question of whether attempt count operates through a distinct channel from semantic task context.

## Gaps / what they didn't do
- Focused exclusively on *retrieval* quality, not on downstream agent behavior change given the retrieved temporal context.
- Does not study how an agent *uses* temporal metadata once retrieved — only whether it can find the right session.
- No task-completion or tool-use efficiency metric; no concept of "reducing turns."
- Does not examine whether attempt count (as opposed to calendar time) changes decision-making.
- Dataset is two-agent conversation logs, not iterative tool-use / debugging loops.
- Single-hop temporal queries only (except time+content set); no multi-step temporal reasoning across attempts.

## Key quotes
> "Conversational meta-data based queries... require the model to retrieve information about previous conversations based on time or the order of a conversational event (e.g., the third conversation on Tuesday)."

> "The semantic retrieval model failed the time-based queries completely, which is to be expected since it uses embedding vectors that carry no information about the meta-data of the response."

> "Session number ('What did we discuss in session/discussion/conversation N?') [is one of the temporal query types]."

## Citation
Alonso, N., Figliolia, T., Ndirango, A., & Millidge, B. (2024). Toward Conversational Agents with Context and Time Sensitive Long-term Memory. arXiv:2406.00057.
