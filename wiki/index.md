# Research Wiki: Temporal Signaling in LLM Debugging Agents

This wiki documents the literature, concepts, experimental design, and in-progress paper draft for a study examining whether giving an LLM agent knowledge of its attempt count changes debugging efficiency.

---

## Papers

| arXiv ID | Title | Relevance | One-line summary |
|---|---|---|---|
| 2309.02427 | Cognitive Architectures for Language Agents (CoALA) | High | Unified framework mapping LLM agents onto memory types and decision cycles; attempt count maps directly onto CoALA's working-memory and metareasoning gaps. |
| 2303.17651 | Self-Refine: Iterative Refinement with Self-Feedback | High | Single LLM iteratively critiques and rewrites its own output, improving quality ~20% across 7 tasks; iteration count (not time) is the operative variable. |
| 2310.08560 | MemGPT: Towards LLMs as Operating Systems | Medium | OS-style hierarchical memory lets agents self-direct paging via function calls; FIFO queue depth is a structural analogue to attempt count. |
| 2502.06975 | Episodic Memory is the Missing Piece for Long-Term LLM Agents | Medium | Position paper arguing episodic memory's five properties (incl. temporal ordering) are not met by any existing LLM architecture; ordinal event index is the tractable retrieval cue. |
| 2402.17753 | Evaluating Very Long-Term Conversational Memory of LLM Agents (LoCoMo) | Medium | Benchmark showing LLMs score ~20% F1 on temporal reasoning vs. ~93% for humans; elapsed time is consistently the hardest signal for models to use. |
| 2406.00057 | Toward Conversational Agents with Context and Time Sensitive Long-term Memory | Medium | Standard semantic RAG fails time-based queries (3–6% recall); ordinal session number retrieval reaches 90% recall, validating discrete event indexing over continuous time. |
| 2409.16909 | Enhancing Temporal Sensitivity and Reasoning for Time-Sensitive QA (TSQA) | Medium | Training framework (TIAE + GCRL) improves temporal QA up to 30% EM; distinguishes sensitivity failures (ignoring time tokens) from reasoning failures (wrong temporal interval). |
| 2310.13420 | Conversation Chronicles: Diverse Temporal and Relational Dynamics | Low | 1M-dialogue dataset showing elapsed-time labels shift agent responses qualitatively, but relationship type dominates; supports event-count over continuous time as the operative signal. |

---

## Concept Pages

- [Temporal Signaling in LLM Agents](concepts/temporal_signaling.md) — What it means to give an LLM a temporal signal, the taxonomy of signal types, and what the literature says about each.
- [Attempt Budgets](concepts/attempt_budget.md) — Definition, cognitive psychology analogy, literature review, and our experimental finding.

---

## Experiment Pages

- `experiment/design.md` — Experimental design, groups A/B/C, stimuli, and procedure (to be created).
- [Experiment Results](experiment/results.md) — Quantitative results: solve rate, tool-use turns, statistical tests for both Claude Sonnet and Claude Opus.
- [CoT Mechanism Analysis](experiment/cot_mechanism.md) — Does the model verbalize the signal (H1) or use it implicitly (H2)? In-progress.
- [CoT Findings](experiment/cot_findings.md) — **H2 confirmed**: anchoring, not explicit cognition. Group C reasons 20% shorter without verbalizing the signal.
- `experiment/stimuli.md` — HumanEvalPack problem set, selection criteria, difficulty distribution (to be created).

---

## Log

<!-- Log entries go here. Format: YYYY-MM-DD | author | note -->
| 2026-04-29 | experiment | Opus experiment completed. Model-capability interaction discovered. Temporal signals decrease turns in Sonnet (p=0.003) but increase turns in Opus (p=0.012) — opposite directions. results.md created. |
