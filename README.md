# Attempt Count, Not Elapsed Time, Reduces Tool-Use Turns in LLM Debugging Agents

> Preprint — work in progress

## Summary

We ask whether injecting temporal signals into an LLM agent's context changes debugging efficiency. In a controlled experiment on HumanEvalPack Python bugs using Claude Code as the agent, we compare three conditions across two model tiers (Sonnet, Opus):

- **Group A:** no temporal signal (control)  
- **Group B:** elapsed time + attempt count  
- **Group C:** attempt count only

**Key findings:**

| | Sonnet (n=100/group) | Opus (n=50/group) |
|---|---|---|
| Solve rate | identical (~99%) | identical (100%) |
| Group C vs A | p=0.003 ✅ fewer turns | p=0.097 ns |
| Group B vs A | p=0.52 ns | p=0.012 ✅ more turns |

Attempt count reduces tool-use turns in Sonnet. Elapsed time adds noise. Opus responds in the opposite direction — temporal signals increase exploratory behavior in frontier models.

## Repo structure

```
runner.py           — experiment runner (Claude Code headless)
analyze.py          — analysis and figures
figures_final.py    — publication-quality figures
bug_injector.py     — bug injection for HumanEvalPack
trial_setup.py      — temp dir setup per trial
results/            — raw .jsonl results per group/run
figures/            — output figures
wiki/               — research knowledge base and paper draft
  papers/           — annotated paper summaries
  concepts/         — synthesis pages
  paper_draft/      — full paper sections
```

## Reproducing

```bash
python -m venv venv && source venv/bin/activate
pip install datasets sentence-transformers pandas numpy matplotlib seaborn scipy tqdm

# Run one group (requires Claude Code CLI logged in)
python runner.py --group A --n 50 --model sonnet

# Analyze
python analyze.py
python figures_final.py
```

## Paper draft

Full paper in [`wiki/paper_draft/paper.md`](wiki/paper_draft/paper.md).

## Status

- [x] Sonnet experiment (n=100/group, 2 runs)
- [x] Opus experiment (n=50/group)
- [ ] Group D (instruction-only ablation) — pending token renewal
- [ ] Offset 50–113 generalization run
- [ ] arXiv submission
