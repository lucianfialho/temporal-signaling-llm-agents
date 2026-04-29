# Paper Draft: Working Outline

## Proposed Titles

1. **"Attempt Count, Not Elapsed Time, Reduces Tool-Use Turns in LLM Debugging Agents"**
   — Declarative; states the Sonnet finding precisely; signals a controlled experiment. May be too narrow now that Opus results complicate the picture.

2. **"Temporal Signaling in LLM Agents: Attempt Budgets Reduce Effort Without Affecting Accuracy"**
   — Broader framing; positions the paper in the temporal-signaling literature; emphasizes the efficiency/accuracy decomposition. Undersells the model-capability interaction.

3. **"Less Is More With Fewer Tries: Attempt Budget Prompting for Efficient LLM Code Repair"**
   — More accessible; "code repair" connects to the HumanEvalPack domain; risks sounding applied rather than scientific.

4. **"Model Capability Moderates Temporal Signal Effects in LLM Debugging Agents"** *(new — reflects Opus replication)*
   — Directly names the interaction finding; positions the paper in the model-scaling literature as well as temporal signaling.

5. **"Attempt Budgets Make Smaller Models Efficient and Larger Models Thorough"** *(new)*
   — Catchy; accurately describes the bidirectional finding; may be too colloquial for a top venue.

**Working title for submission:** Option 4 for NLP/agent venues where the model-capability angle is valued; Option 1 still works as a first-paper subtitle if the Sonnet result is the focus of the primary paper and Opus is a follow-up.

---

## Abstract

LLM agents in iterative loops have no built-in sense of how many attempts they have made. We ask whether injecting this information changes debugging efficiency — and whether the effect depends on model capability.

We ran a controlled experiment on HumanEvalPack Python bugs using Claude Code as the agent, testing three conditions: no temporal signal (control), elapsed time + attempt count (Group B), and attempt count alone (Group C). We replicated across two model tiers: Sonnet (n=100/group) and Opus (n=50/group).

Solve rate was identical across all groups (~98–100%). The effect on tool-use turns was opposite across models: Sonnet's Group C used significantly fewer turns than control (p=0.003, d=0.45), while Opus's Group B used significantly more (p=0.012, d=0.44). Elapsed time added noise for Sonnet and amplified exploration for Opus.

We conclude that attempt count is a low-cost signal with model-dependent effects: it induces efficiency in mid-tier models and exploratory behavior in frontier models — a distinction with direct implications for agent system design.

---

## Section Structure

### 1. Introduction (~600 words)

**Argues:** LLM agents operating in iterative loops lack a natural mechanism for tracking task progress; this omission is not harmless — it leads to inefficient exploration. The paper frames the temporal signaling question as a practical intervention: can a single prompt token reduce agent effort without harming task success? We preview the answer (yes, but only for discrete event count, not continuous elapsed time) and situate the contribution relative to prior work on iterative refinement (Self-Refine), agent memory (CoALA, MemGPT), and temporal reasoning (LoCoMo, TSQA).

### 2. Related Work (~800 words)

**Argues:** The literature splits into three streams that have not been connected: (a) iterative refinement showing that discrete iteration count conditions agent behavior (Self-Refine, CoALA); (b) temporal reasoning showing that elapsed time is a weak LLM signal (LoCoMo, TSQA, TimeMem, Chronicles); and (c) memory architectures showing that discrete event indexing outperforms continuous time for retrieval (TimeMem, MemGPT, Episodic Memory). Our experiment is the first to cross these streams by directly manipulating and isolating elapsed time vs. attempt count in a tool-using debugging agent.

### 3. Experiment Design (~700 words)

**Argues:** The design choices — HumanEvalPack bugs, Claude Code, 3-group between-subjects, 50 problems per group — are well-motivated and sufficient to test the causal claim. This section specifies: (a) the task (Python bug repair with Bash/Read/Edit tools, pass/fail oracle via test suite); (b) the stimuli (HumanEvalPack Python subset, selection criteria, difficulty distribution); (c) the group conditions (exact system prompt text for each group); (d) the dependent variables (solve rate binary, tool-use turns count); (e) the statistical approach (Fisher's exact for solve rate, Mann-Whitney U for turns, alpha=0.05, effect size via Cohen d / rank-biserial correlation).

### 4. Results (~700 words)

**Argues:** Four claims. (a) Solve rate is not significantly different across all groups in either model — the temporal signals do not harm accuracy. (b) For Sonnet, Group C uses significantly fewer tool-use turns than Group A (p=0.003, d≈0.62) — attempt count reduces effort. (c) For Sonnet, Group B does not differ from Group A — elapsed time cancels the count benefit. (d) For Opus, the direction reverses: Group B uses significantly MORE turns than Group A (p=0.012, d=−0.44); Group C trends in the same direction (p=0.097 ns). The section reports means, SDs, test statistics, p-values, and effect sizes for each comparison, for each model. A figure shows the tool-use turn distributions for all three groups, split by model. The result table makes the opposite-direction finding visually obvious.

### 4a. Model Capability Moderates Temporal Signal Effects (~400 words)

**Argues:** The bidirectional finding is not an artifact — it is a theoretically coherent interaction. Three arguments: (i) Opus already uses more turns at baseline (7.62 vs. 7.10 for Sonnet), suggesting its default planning style is more exploratory; temporal signals amplify this tendency rather than constraining it. (ii) The CoALA metareasoning gap predicts exactly this: more capable agents with access to compute-allocation information should allocate *more* computation, not less, because they have the capacity to use it productively. Sonnet, with less capacity, may benefit from the budget as a convergence cue. (iii) The effect is directionally consistent for both signals in Opus (both B and C increase turns relative to A), suggesting this is a property of how Opus processes budget information, not an artifact of the elapsed-time noise mechanism. The section explicitly acknowledges that "more turns" in Opus is not necessarily worse — if Opus's additional turns yield higher-quality fixes or cover more edge cases, the trade-off may be favorable. This is a testable hypothesis for future work (e.g., measuring test pass rate at stricter thresholds, or qualitative analysis of tool call content).

### 5. Discussion (~800 words)

**Argues:** Five interpretive points. First, why does attempt count work for Sonnet? The CoALA metareasoning gap and Self-Refine's diminishing-returns curve both predict front-loaded efficiency gains from discrete iteration awareness — our finding is mechanistically consistent. Second, why does elapsed time hurt (for Sonnet)? The noise hypothesis: LLMs cannot reliably reason about continuous time (LoCoMo: 20% F1; TSQA: 8–17% EM), so elapsed time signals dilute rather than augment the count signal. Third, why does temporal signaling increase turns for Opus? Two non-exclusive mechanisms: (a) Opus's higher baseline capability means it can productively use additional turns, so the budget acts as a license rather than a constraint; (b) Opus may be more sensitive to the metareasoning cue and interprets "you have a budget" as "you should use it well" — which for a capable model means being more thorough, not faster. Fourth, solve rate invariance across both models: consistent with Parkinson's Law — work adjusts to fill available turns without a budget, but the core fix is discoverable either way. Fifth, practical implications: the same prompt token has opposite cost implications depending on model choice. Deployers should consider whether they want Opus to be more exploratory (potentially more thorough) or Sonnet to be more efficient (definitely cheaper).

### 6. Limitations and Future Work (~500 words)

**Argues:** Five limitations. (a) Two models (Claude Sonnet, Claude Opus) but both from a single provider (Anthropic); generalizability to other model families is untested, and the capability-moderation effect may be provider-specific. (b) Unequal sample sizes: Sonnet n=100/group, Opus n=50/group; the Opus results have lower statistical power. (c) Controlled benchmark: HumanEvalPack bugs are well-specified; real-world debugging tasks may differ. (d) Group B confound: elapsed time and the system prompt instruction are covaried in Group B; a Group D (instruction only) would fully decompose the effect. (e) Short-run: we measure within-session turn counts; long-run consolidation (episodic memory → procedural shortcut) is not captured. Future work: replicate Opus at n=100/group for higher power; vary MAX denominator (N/3 vs. N/10); test harder problems where control solve rate is lower; replicate with open-source models (Llama 3, Mistral) at different capability levels to map the capability-moderation curve; study whether more Opus turns actually yield higher-quality fixes (test suite pass rate at stricter thresholds); study multi-session consolidation.

### 7. Conclusion (~250 words)

**Argues:** Temporal signals have capability-dependent effects on LLM debugging agents. For less capable models (Sonnet), attempt count alone is a low-cost intervention that induces efficiency without sacrificing solve rate. For more capable models (Opus), the same signal induces more exploratory behavior — more tool-use turns, not fewer. This bidirectional finding reframes the question from "does temporal signaling help?" to "what does temporal signaling optimize for, and at what capability level?" The result has immediate practical implications: agent system designers should account for model capability when deciding whether and how to inject temporal signals. The finding positions discrete event count — not continuous time — as the operative temporal primitive, and demonstrates that its effect direction depends on the agent's intrinsic metareasoning capacity.

---

## Key Claims to Prove

1. **Causal claim (Sonnet):** `attempt: N/5` in the system prompt *causes* a reduction in tool-use turns in Sonnet (not correlated with some other factor).
2. **Null claim (Sonnet):** Elapsed time does not independently reduce turns (Group B vs. Group A: no significant difference for Sonnet).
3. **Interference claim (Sonnet):** Elapsed time in Group B actively cancels the count benefit seen in Group C (Group B is not significantly better than A, while Group C is).
4. **Reversal claim (Opus):** The same temporal signals that reduce turns in Sonnet *increase* turns in Opus — statistically significant for Group B (p=0.012), trending for Group C (p=0.097).
5. **Capability interaction claim:** The direction of the temporal signal effect is moderated by model capability. This is not a null result in one model — it is an opposite-sign effect.
6. **Accuracy invariance:** The efficiency/exploration shifts are pure behavioral changes — no solve rate tradeoff in either model.

---

## Figures Needed

| Figure | Content | Source |
|---|---|---|
| Fig. 1 | Box plots or violin plots of tool-use turn distributions for Groups A, B, C. Annotate with median lines and p-values for pairwise comparisons. | Experiment results |
| Fig. 2 | Bar chart of solve rate by group (with 95% CI or error bars). Visually confirms null result — bars should be nearly identical. | Experiment results |
| Fig. 3 | Experiment design schematic: three columns (A/B/C), showing system prompt text, signal injected, and arrow to outcome metrics. No data — conceptual figure. | Designed |
| Fig. 4 (optional) | Turn-count distribution as a function of problem difficulty (if difficulty ratings are available for HumanEvalPack problems). Tests whether the effect is concentrated in medium-difficulty problems. | Experiment results × HumanEvalPack difficulty metadata |
| Fig. 5 (optional) | Literature positioning 2x2: x-axis = signal type (continuous time / discrete count), y-axis = task type (conversational / tool-using). Places each cited paper and our experiment in one quadrant. | Designed |

---

## Submission Targets (Tentative)

- **Primary:** EMNLP 2025 or ACL 2026 (NLP venue with strong agent/memory track).
- **Alternative:** NeurIPS 2025 workshop on LLM agents or ICLR 2026.
- **Preprint:** arXiv submission concurrent with first submission.
