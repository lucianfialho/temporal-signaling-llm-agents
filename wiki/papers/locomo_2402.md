---
arxiv: 2402.17753
title: "Evaluating Very Long-Term Conversational Memory of LLM Agents"
authors: Maharana et al.
year: 2024
tags: [long-term-memory, conversational-agents, temporal-reasoning, RAG, evaluation-benchmark, dialogue]
relevance: medium
---

## One-line summary
LoCoMo is a dataset of 50 synthetic long-term dialogues (avg. 300 turns, 9K tokens, up to 35 sessions) paired with a QA/summarization/multimodal benchmark, revealing that LLMs consistently fail at temporal reasoning across long conversation histories.

## What they did
Built a human-machine pipeline to generate very long-term dialogues: GPT-3.5 agents were given unique personas and temporal event graphs (causally linked life events over 6–12 months), then generated multi-session dialogues using a reflect-and-respond architecture (short-term session summaries + long-term observation retrieval). Human annotators fixed ~15% of turns and ~19% of images. The resulting dataset was used to benchmark base LLMs, long-context LLMs (GPT-3.5-turbo-16K), and RAG systems across three tasks: QA (5 question types), event graph summarization, and multimodal dialogue generation.

## Key findings
- Temporal reasoning is the hardest QA category across all model types; long-context models score only ~20% F1 on temporal questions vs. ~93% for humans.
- Long-context LLMs (16K window) improve overall QA (+66% over base) but collapse on adversarial questions (2.1% vs. 22% for base models) — they hallucinate when exposed to long contexts.
- RAG with observations (atomic assertions about speaker life events) outperforms RAG with raw dialogue turns or session summaries; signal-to-noise ratio in retrieved context is the critical variable.
- Event summarization: long-context models underperform base models despite larger windows (precision −3%, recall −8.7%), suggesting long-context models do not accurately utilize extended context.
- Five error categories in LLM event summarization: missing temporal/causal connections, hallucination, misunderstanding of dialog cues (humor/sarcasm), wrong speaker attribution, and treating unimportant events as salient.
- "The way a system responds about past events can vary depending on the amount of time that has passed since the last conversation" — identified as a core challenge but not solved.

## Relevance to our experiment
How this connects to: "attempt count (not elapsed time) reduces agent tool-use turns in debugging tasks"

The connection is indirect but substantive:

1. **Direct evidence that elapsed time is a poor signal for LLMs.** LoCoMo's central finding is that LLMs cannot reliably reason about temporal intervals between events. The benchmark explicitly includes "temporal reasoning" as a question type, and this is consistently the worst-performing category. If LLMs cannot track elapsed time in dialogue, they are equally unlikely to use elapsed wall-clock time as a reliable planning signal in agentic debugging tasks.

2. **Attempt count as a count-based (not time-based) signal.** LoCoMo's event graph architecture uses discrete, ordinal events — not continuous time. The agents are conditioned on "events that occur between the last and current session," i.e., a discrete event count, not a timestamp. This mirrors how attempt count discretizes agent progress. The paper implicitly validates count/event-based memory over time-based memory.

3. **Retrieval unit matters for efficiency.** The finding that observation-level RAG (atomic facts about speaker state) outperforms raw-turn or summary RAG is analogous to our experiment: a compact, structured signal (attempt count, i.e., "how many times has this agent tried?") outperforms a continuous, noisy signal (elapsed time). Both findings point to the same principle: discrete, semantically dense signals beat continuous temporal signals for LLM conditioning.

4. **Adversarial hallucination under long context.** When agents are given more context (longer history), they hallucinate more on adversarial questions. In debugging tasks, an agent that counts elapsed time accumulates a growing, potentially confounding context. An agent that tracks attempt count has a single, incrementing integer — a minimal and non-confounding signal.

## Gaps / what they didn't do
- Only evaluates conversational/dialogue agents, not task-completing or tool-using agents.
- Does not study how temporal signals affect agent *behavior* (action selection), only agent *comprehension* (answer accuracy).
- Elapsed time is embedded in the event graph structure but is never tested as an isolated independent variable against other signals.
- No agentic loops — the benchmark is evaluative (Q&A), not generative in the agent sense (plan-act-observe cycles).
- Does not study attempt count or iteration count as a memory signal at all.
- Temporal reasoning failure is documented but no mechanism or fix is proposed beyond "use RAG with observations."
- Dataset is English-only and synthetic (LLM-generated with human edits); real-world temporal reasoning may differ.

## Key quotes
> "LLMs face challenges in understanding time concepts within dialogues, which is consistent with findings from other single-turn-based benchmarks focused on temporal reasoning capabilities for LLMs."

> "The interesting finding is that time reasoning and open-domain knowledge questions are the most challenging scenarios."

> "Reasoning over time intervals presents challenges. For example, the way a system responds about past events can vary depending on the amount of time that has passed since the last conversation."

> "There is a noticeable 5% improvement with gpt-3.5-turbo when the input is top 5 relevant observations instead of pure conversation logs. This improvement falters with an increase in the number of retrieved observations, suggesting that it is important to reduce the signal-to-noise (SNR) ratio in retrieved contexts."

> "Long-context LLMs can comprehend longer narratives, yet they are prone to generating hallucinations... performance on adversarial questions drops to a mere 2.1%."

## Citation
Maharana, A., Lee, D.-H., Tulyakov, S., Bansal, M., Barbieri, F., & Fang, Y. (2024). Evaluating Very Long-Term Conversational Memory of LLM Agents. *arXiv preprint arXiv:2402.17753*.
