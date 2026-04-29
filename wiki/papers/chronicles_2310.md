---
arxiv: 2310.13420
title: "Conversation Chronicles: Towards Diverse Temporal and Relational Dynamics in Multi-Session Conversations"
authors: Jihyoung Jang et al.
year: 2023
tags: [multi-session-dialogue, temporal-dynamics, dataset, long-term-memory, conversational-agents]
relevance: low
---

## One-line summary
A 1M-dialogue dataset and model (ReBot) that forces explicit time-interval and speaker-relationship conditioning across multi-session conversations, showing that named elapsed time changes agent behavior.

## What they did
Built Conversation Chronicles: 200K episodes, each with 5 sessions, where every session is labeled with a time interval (few hours / days / weeks / months / years) and a fine-grained speaker relationship (10 categories). Dialogues were distilled from ChatGPT via structured prompts. Trained ReBot (T5-base summarizer + BART-large generator, ~630M total parameters) on this data. Evaluated with human annotators on coherence, consistency, time-interval plausibility, relationship maintenance, engagingness, humanness, and memorability.

## Key findings
- Elapsed-time labels shift model responses qualitatively: models trained with time info produce interval-specific answers ("we've been planning it for months"), while models trained without produce generic answers ("a long time").
- Speaker relationship is the dominant factor in shaping dialogue style and content; same opening utterance, different relationship, different conversational trajectory.
- ReBot outperforms MSC 2.7B on all human-rated metrics despite fewer parameters.
- Ablation confirms both temporal and relational conditioning are individually necessary; their combination is additive.
- Average human evaluation score: 4.34/5 for dataset quality; 4.55/5 for ReBot generation quality.

## Relevance to our experiment
How this connects to: "attempt count (not elapsed time) reduces agent tool-use turns in debugging tasks"

Weak but non-zero relevance. Chronicles demonstrates that when elapsed time is made explicit in the context, it changes agent behavior — but the mechanism is label injection ("a few months later"), not genuine temporal awareness. Our hypothesis inverts this: we are testing whether *event count* (attempts) is the operative variable, not wall-clock elapsed time. Chronicles provides a useful negative control framing: even in a system that explicitly encodes elapsed time, what drives behavioral change is really the event sequence encoded alongside it (session N-1 summary + time label). This supports the idea that discrete event count, not duration, is the tractable signal.

## Gaps / what they didn't do
- Never tests whether models can infer time from events alone (no elapsed-time label provided).
- Multi-session setup is conversational QA, not task-completion or tool-use agents — no action loops.
- No attempt count variable; all temporal signal is externally supplied at training time.
- Evaluation is human preference, not task success rate or efficiency (turns-to-completion).
- Does not distinguish between "elapsed time" and "number of events since last session."

## Key quotes
> "When the model is trained devoid of time interval data, it exhibits a trend toward producing responses with generic time information."

> "Time interval plays an important role to infuse dynamics in a conversational interaction between speakers. For instance, depending on the time elapsed since the last conversation, their responses about past events would vary."

## Citation
Jang, J., Boo, M., & Kim, H. (2023). Conversation Chronicles: Towards Diverse Temporal and Relational Dynamics in Multi-Session Conversations. arXiv:2310.13420.
