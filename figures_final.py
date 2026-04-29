"""
Final publication figures for the paper.
"""

import json, glob, numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats
from collections import defaultdict
from pathlib import Path

Path("figures").mkdir(exist_ok=True)

COLORS = {"A": "#6B7280", "B": "#3B82F6", "C": "#F59E0B"}
LABELS = {"A": "Control", "B": "Time+Count", "C": "Count only"}
plt.rcParams.update({"font.family": "sans-serif", "font.size": 11})

# ── Load data ─────────────────────────────────────────────────────────────────
def load(model):
    data = defaultdict(dict)
    if model == "sonnet":
        files = (
            glob.glob("results/run[12]_sonnet_group_*.jsonl") +
            ["results/group_A_20260428_184037.jsonl",
             "results/group_B_20260428_191814.jsonl",
             "results/group_C_20260428_195820.jsonl",
             "results/run2_group_A_20260428_224235.jsonl",
             "results/run2_group_B_20260429_071427.jsonl",
             "results/run2_group_C_20260429_071427.jsonl"]
        )
    else:
        files = glob.glob("results/run1_opus_group_*.jsonl")

    for f in files:
        grp = next((g for g in "ABC" if f"group_{g}_" in f or f"group_{g}." in f), None)
        if not grp: continue
        for line in open(f):
            r = json.loads(line)
            if not r["task_id"].startswith("Python/"): continue
            if "num_turns" not in r: continue
            key = f"{r['task_id']}_run{r.get('run_id',1)}"
            if key not in data[grp]:
                data[grp][key] = r
    return {g: list(data[g].values()) for g in "ABC"}


sonnet = load("sonnet")
opus   = load("opus")


# ── Fig 1: Turns distribution — Sonnet vs Opus side by side ──────────────────
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)

for ax, (model_data, title, n_label) in zip(axes, [
    (sonnet, "Sonnet (n=100/group)", "n=100"),
    (opus,   "Opus (n=50/group)",   "n=50"),
]):
    positions = [1, 2, 3]
    parts = ax.violinplot(
        [np.array([r["num_turns"] for r in model_data[g]]) for g in "ABC"],
        positions=positions,
        showmedians=True,
        showextrema=False,
    )
    for pc, grp in zip(parts["bodies"], "ABC"):
        pc.set_facecolor(COLORS[grp])
        pc.set_alpha(0.7)
    parts["cmedians"].set_color("black")
    parts["cmedians"].set_linewidth(2)

    # overlay means
    for pos, grp in zip(positions, "ABC"):
        turns = [r["num_turns"] for r in model_data[grp]]
        ax.scatter([pos], [np.mean(turns)], color="white", edgecolor=COLORS[grp],
                   s=60, zorder=5, linewidth=2)

    ax.set_xticks(positions)
    ax.set_xticklabels([LABELS[g] for g in "ABC"])
    ax.set_title(title, fontweight="bold")
    ax.set_ylabel("Tool-use turns" if ax == axes[0] else "")
    ax.spines[["top","right"]].set_visible(False)

    # significance brackets
    def bracket(ax, x1, x2, y, p):
        sig = "**" if p < 0.01 else ("*" if p < 0.05 else "ns")
        h = 0.3
        ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.2, color="black")
        ax.text((x1+x2)/2, y+h+0.05, sig, ha="center", va="bottom", fontsize=10)

    all_turns = [r["num_turns"] for g in "ABC" for r in model_data[g]]
    ymax = max(all_turns) + 1.5

    if title.startswith("Sonnet"):
        _, p_ac = stats.mannwhitneyu(
            [r["num_turns"] for r in model_data["A"]],
            [r["num_turns"] for r in model_data["C"]], alternative="two-sided")
        bracket(ax, 1, 3, ymax, p_ac)
    else:
        _, p_ab = stats.mannwhitneyu(
            [r["num_turns"] for r in model_data["A"]],
            [r["num_turns"] for r in model_data["B"]], alternative="two-sided")
        bracket(ax, 1, 2, ymax, p_ab)

fig.suptitle("Tool-Use Turns by Temporal Signal Condition", fontsize=13, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("figures/fig1_turns_violin.png", dpi=200, bbox_inches="tight")
plt.close()
print("✓ fig1_turns_violin.png")


# ── Fig 2: Mean turns comparison bar chart ────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=False)

for ax, (model_data, title) in zip(axes, [
    (sonnet, "Sonnet"),
    (opus,   "Opus"),
]):
    groups = list("ABC")
    means  = [np.mean([r["num_turns"] for r in model_data[g]]) for g in groups]
    sems   = [np.std([r["num_turns"] for r in model_data[g]]) /
              np.sqrt(len(model_data[g])) for g in groups]

    bars = ax.bar(groups, means, yerr=sems, capsize=4, width=0.5,
                  color=[COLORS[g] for g in groups], edgecolor="white")

    for bar, m in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
                f"{m:.2f}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_xticklabels([LABELS[g] for g in groups], fontsize=9)
    ax.set_title(title, fontweight="bold")
    ax.set_ylabel("Mean tool-use turns")
    ax.set_ylim(0, max(means) + 1.5)
    ax.spines[["top","right"]].set_visible(False)

fig.suptitle("Mean Tool-Use Turns ± SEM", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig("figures/fig2_means_bar.png", dpi=200, bbox_inches="tight")
plt.close()
print("✓ fig2_means_bar.png")


# ── Fig 3: Direction-of-effect summary ────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 3.5))

models  = ["Sonnet\n(n=100)", "Opus\n(n=50)"]
deltas_c = [
    np.mean([r["num_turns"] for r in sonnet["C"]]) - np.mean([r["num_turns"] for r in sonnet["A"]]),
    np.mean([r["num_turns"] for r in opus["C"]])   - np.mean([r["num_turns"] for r in opus["A"]]),
]
deltas_b = [
    np.mean([r["num_turns"] for r in sonnet["B"]]) - np.mean([r["num_turns"] for r in sonnet["A"]]),
    np.mean([r["num_turns"] for r in opus["B"]])   - np.mean([r["num_turns"] for r in opus["A"]]),
]

x = np.arange(len(models))
w = 0.3
ax.bar(x - w/2, deltas_c, w, label="Count only vs. Control",
       color=COLORS["C"], edgecolor="white")
ax.bar(x + w/2, deltas_b, w, label="Time+Count vs. Control",
       color=COLORS["B"], edgecolor="white")

ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.set_xticks(x)
ax.set_xticklabels(models)
ax.set_ylabel("Δ turns vs. control\n(negative = fewer turns)")
ax.set_title("Effect Direction by Model Tier", fontweight="bold")
ax.legend(frameon=False, fontsize=9)
ax.spines[["top","right"]].set_visible(False)

# annotate significance
sigs = [("*", -0.15), ("ns", 0.05), ("ns", -0.15), ("*", 0.6)]
positions = [(0-w/2, deltas_c[0]), (0+w/2, deltas_b[0]),
             (1-w/2, deltas_c[1]), (1+w/2, deltas_b[1])]
labels_sig = ["**", "ns", "ns", "*"]
for (xi, yi), sig in zip(positions, labels_sig):
    offset = -0.25 if yi < 0 else 0.08
    ax.text(xi, yi + offset, sig, ha="center", fontsize=10, fontweight="bold")

plt.tight_layout()
plt.savefig("figures/fig3_direction.png", dpi=200, bbox_inches="tight")
plt.close()
print("✓ fig3_direction.png")

print("\nAll figures saved to figures/")
