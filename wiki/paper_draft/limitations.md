# Limitations

**Single provider.** Both models tested are from the same provider (Anthropic). The effect may not generalize to GPT-4o, Gemini, or open-source models such as Llama 3 or Mistral. The capability-moderation finding — that the effect direction reverses between model tiers — requires replication with models from different providers and training pipelines before it can be claimed as a general principle.

**Unequal sample sizes.** Sonnet was tested with n=100 per group across two independent runs; Opus with n=50 in a single run. The Opus results are less statistically powered, and the Group C trend (p=0.097) falls below the significance threshold. A fully powered Opus replication would require approximately 100 trials per group to match Sonnet's precision.

**Group B confound.** Group B mixes two manipulations: a prefix token with elapsed time and attempt count, and an additional system prompt instruction to adapt strategy based on time. We cannot disentangle whether the null effect in Sonnet (and the positive effect in Opus) is driven by the time value, the attempt count, or the instruction. A fourth group — instruction only, no temporal signal — would cleanly decompose this.

**Benchmark scope.** HumanEvalPack bugs are synthetic, small (typically 5–30 lines), and drawn from a well-known dataset likely present in the models' training data. Real-world debugging tasks involve larger codebases, ambiguous specifications, and bugs that require multi-file reasoning. Whether the attempt-count effect scales to harder, longer tasks is unknown.

**Unobservable mechanism.** Our interpretation of *why* attempt count affects Opus and Sonnet differently is based on aggregate turn counts. We cannot observe the agent's internal reasoning, confirm that it attended to the temporal signal, or verify that the extra turns in Opus correspond to exploration rather than confusion. Mechanistic studies using chain-of-thought traces or activation analysis would be needed to validate the proposed explanation.
