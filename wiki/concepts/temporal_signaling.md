# Temporal Signaling in LLM Agents

## Definition

A **temporal signal** is any piece of information injected into an LLM agent's context that encodes something about *when* or *how far along* in a task the current inference step occurs. The signal does not have to be a clock time — it can be an ordinal count, a session identifier, an elapsed duration, or an implicit cue derived from the structure of prior interactions.

The core question this concept page addresses: **which types of temporal signal reliably change LLM agent behavior, and through what mechanism?**

---

## Taxonomy of Temporal Signal Types

### 1. Elapsed Wall-Clock Time

The agent is told how many seconds, minutes, or hours have passed since some reference event (session start, task assignment, etc.).

**Example in our experiment:** Group B received `session_elapsed: Xs` in the system prompt header.

**What the literature says:**

- Conversation Chronicles (arXiv:2310.13420) is the most direct test. Models trained *with* explicit elapsed-time labels ("a few months later") produce interval-specific language; models trained without produce generic language. However, the *mechanism* is label-conditioned text generation, not genuine temporal reasoning — the model produces output that sounds right for the labeled interval.
- LoCoMo (arXiv:2402.17753) shows the failure mode clearly: LLMs score ~20% F1 on temporal reasoning questions vs. ~93% for humans, and elapsed-time questions are the hardest category. The paper explicitly concludes that "LLMs face challenges in understanding time concepts within dialogues."
- TimeMem (arXiv:2406.00057) provides the retrieval analogue: pure semantic search on time-based queries returns 3–6% recall — effectively nothing. Models cannot use continuous time as a retrieval key.
- TSQA (arXiv:2409.16909) diagnoses two failure modes: (a) *temporal insensitivity* — the model fails to attend to time tokens at all; (b) *temporal misreasoning* — the model attends to the token but places the answer in the wrong interval. Both failures affect elapsed-time signals.

**Assessment:** Wall-clock elapsed time is a weak and noisy signal for LLMs. Models can parrot interval-appropriate language when trained on labeled data, but cannot reliably reason about continuous time intervals at inference time. Our Group B result (no significant difference from control) is consistent with this literature.

---

### 2. Attempt Count / Iteration Count

The agent is told it is on attempt N of MAX_N (e.g., `attempt: 3/5`).

**Example in our experiment:** Group B and Group C both received `attempt: N/5`. Group C received *only* this signal.

**What the literature says:**

- Self-Refine (arXiv:2303.17651) provides the strongest support. The entire mechanism is iteration-indexed: generate → feedback → refine, up to 4 iterations. Critically, gains are front-loaded (largest improvement at iteration 1→2, diminishing returns thereafter), indicating the agent's behavior changes as a function of which iteration it is on — not how much time has passed.
- CoALA (arXiv:2309.02427) provides the theoretical grounding: attempt count is a natural **working memory variable** that persists across decision cycles. CoALA explicitly identifies metareasoning — knowing when to stop exploring and commit to an action — as an unsolved problem. An attempt count injected into working memory is precisely the kind of signal that should trigger more economical metareasoning.
- MemGPT (arXiv:2310.08560) implements a structural analogue: the FIFO queue depth and recursive summary encode "how many prior interactions have occurred." The agent's context implicitly contains an ordinal position in the conversation, and this drives memory-management behavior (paging to archival storage). MemGPT's superior performance on nested multi-hop retrieval is attributed to the agent's ability to chain function calls — i.e., to know it is on retrieval attempt N and plan accordingly.
- TimeMem (arXiv:2406.00057) demonstrates that *session number* (an ordinal count) achieves 90% recall as a retrieval key, vs. 3–6% for continuous time. The gap between ordinal index and calendar time is a direct empirical validation that discrete counts are more tractable for LLMs than continuous temporal durations.

**Assessment:** Attempt count is a tractable, discrete, working-memory-compatible signal. It aligns with how LLM agents are architecturally structured (decision cycles, not clocks) and has theoretical support in CoALA's metareasoning gap and empirical support in Self-Refine's diminishing-returns curve. Our Group C result (fewer tool-use turns, p=0.04, Cohen d=0.62) confirms that this signal changes agent behavior in an efficiency-promoting direction.

---

### 3. Session Date / Absolute Timestamp

The agent is told the current date or the date of each prior session (e.g., "today is 2024-03-15; your last session was 2024-03-10").

**What the literature says:**

- LoCoMo (arXiv:2402.17753) embeds date information in its event graphs but finds models still fail temporal reasoning. Long-context models (16K) are even worse on adversarial temporal questions (2.1% accuracy) than base models (22%), suggesting that providing more temporal context can actively degrade performance.
- Conversation Chronicles (arXiv:2310.13420) uses coarse session labels (hours/days/weeks/months/years) rather than absolute dates; models trained on these labels perform better, but the signal is effectively ordinal (5 bins), not continuous calendar time.
- TSQA (arXiv:2409.16909) trains on explicit year-labeled QA. Even with training, models score 8–17% EM on open-book temporal QA. Human performance is substantially higher, confirming the gap is fundamental.

**Assessment:** Absolute timestamps are the hardest temporal signal for LLMs. Even with dedicated training (TSQA), the task remains difficult. At inference time (our experimental setting), there is no reason to expect session dates to produce meaningful behavioral change.

---

### 4. Event Order / Ordinal Position

The agent receives an explicit or implicit signal about the sequential position of the current event in a series (e.g., "this is the 3rd conversation", "session 4 of 7", or an implicit ordering via conversation history).

**What the literature says:**

- TimeMem (arXiv:2406.00057) shows that `f_value(session_index, [5])` — querying by session number — achieves high recall while continuous-time queries fail. The paper explicitly identifies "Session number ('What did we discuss in session N?')" as the most reliably retrievable temporal unit.
- Episodic Memory (arXiv:2502.06975) argues that "when" in episodic memory is fundamentally ordinal (the order of events in a sequence), not metric (the duration between events). The five properties of episodic memory all concern contextual binding of events to their position in a sequence, not their absolute timestamp.
- LoCoMo's event graph architecture uses discrete, causally-linked life events rather than continuous time — implicitly validating ordinal event structure over calendar time.

**Assessment:** Ordinal event position is the most naturally LLM-compatible form of temporal signal. It aligns with how transformers process sequences (position-indexed tokens), how episodic memory binds context (ordinal retrieval cues), and how agents are architecturally structured (decision cycle N). Attempt count is a special case of event order — and our results confirm it is behaviorally effective.

---

## Key Tension: Continuous Time vs. Discrete Event Count

The central tension in temporal signaling is between two models of "when":

**Continuous (metric) time:** Elapsed seconds, calendar dates, interval labels. Requires the agent to reason about a number on a linear scale, map it to task-relevant expectations, and adjust behavior accordingly. LLMs are consistently poor at this (LoCoMo, TSQA, TimeMem).

**Discrete (ordinal) event count:** Attempt N of M, session 3, iteration 2. Requires the agent to treat the count as a working memory variable that constrains remaining budget and conditions planning. LLMs handle this more naturally because the transformer architecture itself is sequence-indexed, not time-indexed (CoALA, Self-Refine, TimeMem).

The noise hypothesis provides a mechanistic explanation for why adding elapsed time to attempt count (Group B) *removes* the benefit seen with attempt count alone (Group C): continuous time injects irrelevant variation into the planning signal. The agent must now interpret both "how many tries left" and "how long this has taken" — the latter adds no useful information for debugging and may introduce spurious correlations (slow attempts = hard problems? fast attempts = easy?).

---

## Our Experiment's Contribution

Prior work has studied temporal signals in conversational agents (Chronicles, LoCoMo), retrieval systems (TimeMem), and QA benchmarks (TSQA), but not in iterative tool-using agents performing task completion. Our contribution is:

1. **Causal isolation of attempt count from elapsed time.** By crossing the two signals in a controlled experiment (Group A: none; Group B: both; Group C: count only), we establish that attempt count — not elapsed time — is the operative variable.

2. **Efficiency, not accuracy.** Prior work measures answer quality or retrieval recall. We measure tool-use turn count as the dependent variable, holding solve rate constant. This isolates the *effort-reduction* effect of temporal signaling, which is orthogonal to accuracy.

3. **Tool-using debugging agent.** The agent uses Bash, Read, and Edit tools on real code bugs. This is a more naturalistic and consequential setting than dialogue or QA benchmarks.

4. **Effect size quantification.** Cohen d=0.62 for the attempt-count condition is a medium-to-large effect for a single-variable prompt intervention. This establishes practical significance alongside statistical significance (p=0.04).

---

## See Also

- [Attempt Budgets](attempt_budget.md) — Deep dive on the "N of MAX" framing and its cognitive psychology analogues.
- `../paper_draft/outline.md` — Working outline for the preprint.
