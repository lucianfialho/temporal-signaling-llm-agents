"""
Analysis for agentic experiment results.

New schema per trial:
  task_id, group, bug_desc, solved, num_turns, elapsed_call, total_time
"""

import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

RESULTS_DIR = Path("results")
FIGS_DIR    = Path("figures")
FIGS_DIR.mkdir(exist_ok=True)

PALETTE = {"A": "#888888", "B": "#2196F3", "C": "#FF9800"}
GROUP_LABELS = {
    "A": "A — control",
    "B": "B — time+attempt",
    "C": "C — attempt only",
}

# ── Load ──────────────────────────────────────────────────────────────────────
def load_results(files: list[Path]) -> pd.DataFrame:
    rows = []
    seen = set()  # deduplicate (task_id, group)
    for f in sorted(files):
        with open(f) as fh:
            for line in fh:
                r = json.loads(line)
                key = (r["task_id"], r["group"])
                if key in seen:
                    continue
                seen.add(key)
                rows.append({
                    "task_id":      r["task_id"],
                    "group":        r["group"],
                    "bug_desc":     r.get("bug_desc", ""),
                    "solved":       bool(r.get("solved", False)),
                    "num_turns":    int(r.get("num_turns", 1)),
                    "elapsed_call": float(r.get("elapsed_call", 0)),
                    "total_time":   int(r.get("total_time", 0)),
                    "error":        r.get("error"),
                })
    return pd.DataFrame(rows)


# ── Plot 1: Solve rate ────────────────────────────────────────────────────────
def plot_solve_rate(df: pd.DataFrame):
    rates = (df.groupby("group")["solved"]
               .agg(["mean", "count", "sum"])
               .reset_index())
    rates.columns = ["group", "rate", "n", "solved_n"]

    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(rates["group"], rates["rate"],
                  color=[PALETTE[g] for g in rates["group"]], width=0.5)
    for bar, row in zip(bars, rates.itertuples()):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01,
                f"{row.rate:.1%}\n({row.solved_n}/{row.n})",
                ha="center", va="bottom", fontsize=10)

    ax.set_title("Solve Rate by Group", fontsize=13)
    ax.set_ylabel("Proportion Solved")
    ax.set_xlabel("Group")
    ax.set_ylim(0, 1.1)
    ax.set_xticklabels([GROUP_LABELS[g] for g in rates["group"]], fontsize=9)
    plt.tight_layout()
    plt.savefig(FIGS_DIR / "solve_rate.png", dpi=150)
    plt.close()
    print("✓ solve_rate.png")


# ── Plot 2: Turns distribution ────────────────────────────────────────────────
def plot_turns(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    # All problems
    sns.boxplot(data=df, x="group", y="num_turns",
                palette=PALETTE, ax=axes[0])
    axes[0].set_title("Tool-Use Turns — All Problems")
    axes[0].set_ylabel("# Internal Turns")
    axes[0].set_xlabel("")
    axes[0].set_xticklabels([GROUP_LABELS[g] for g in df["group"].unique()], fontsize=8)

    # Solved only
    solved = df[df["solved"]]
    if not solved.empty:
        sns.boxplot(data=solved, x="group", y="num_turns",
                    palette=PALETTE, ax=axes[1])
        axes[1].set_title("Tool-Use Turns — Solved Problems Only")
        axes[1].set_ylabel("# Internal Turns")
        axes[1].set_xlabel("")
        axes[1].set_xticklabels([GROUP_LABELS[g] for g in solved["group"].unique()], fontsize=8)

    plt.tight_layout()
    plt.savefig(FIGS_DIR / "turns_distribution.png", dpi=150)
    plt.close()
    print("✓ turns_distribution.png")


# ── Plot 3: Time to solve ─────────────────────────────────────────────────────
def plot_time(df: pd.DataFrame):
    solved = df[df["solved"]]
    if solved.empty:
        return
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(data=solved, x="group", y="elapsed_call",
                palette=PALETTE, ax=ax)
    ax.set_title("Time to Solve (seconds)")
    ax.set_ylabel("Elapsed (s)")
    ax.set_xlabel("")
    ax.set_xticklabels([GROUP_LABELS[g] for g in solved["group"].unique()], fontsize=8)
    plt.tight_layout()
    plt.savefig(FIGS_DIR / "time_to_solve.png", dpi=150)
    plt.close()
    print("✓ time_to_solve.png")


# ── Plot 4: Turns by bug type ──────────────────────────────────────────────────
def plot_by_bug_type(df: pd.DataFrame):
    if df["bug_desc"].nunique() < 2:
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    order = df.groupby("bug_desc")["num_turns"].mean().sort_values(ascending=False).index
    sns.barplot(data=df, x="bug_desc", y="num_turns", hue="group",
                order=order, palette=PALETTE, ax=ax)
    ax.set_title("Avg Turns by Bug Type and Group")
    ax.set_xlabel("Bug Type")
    ax.set_ylabel("Avg # Turns")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(FIGS_DIR / "turns_by_bug_type.png", dpi=150)
    plt.close()
    print("✓ turns_by_bug_type.png")


# ── Stats summary ─────────────────────────────────────────────────────────────
def print_summary(df: pd.DataFrame):
    lines = ["=" * 55, "EXPERIMENT RESULTS", "=" * 55]

    for g in ["A", "B", "C"]:
        gdf = df[df["group"] == g]
        if gdf.empty:
            continue
        solved = gdf[gdf["solved"]]
        lines.append(f"\nGroup {g} — {GROUP_LABELS[g]}  (n={len(gdf)})")
        lines.append(f"  Solve rate:       {gdf['solved'].mean():.1%}  ({gdf['solved'].sum()}/{len(gdf)})")
        lines.append(f"  Avg turns (all):  {gdf['num_turns'].mean():.1f}  ± {gdf['num_turns'].std():.1f}")
        if not solved.empty:
            lines.append(f"  Avg turns (solved): {solved['num_turns'].mean():.1f}")
            lines.append(f"  Avg time (solved):  {solved['elapsed_call'].mean():.0f}s")

    lines.append("\n" + "=" * 55)
    lines.append("STATISTICAL TESTS")
    lines.append("=" * 55)

    groups = {g: df[df["group"] == g] for g in ["A", "B", "C"]}

    # Solve rate: chi-square
    for g1, g2 in [("A", "B"), ("A", "C"), ("B", "C")]:
        d1, d2 = groups[g1]["solved"], groups[g2]["solved"]
        if d1.empty or d2.empty:
            continue
        table = [[d1.sum(), len(d1) - d1.sum()],
                 [d2.sum(), len(d2) - d2.sum()]]
        chi2, p, _, _ = stats.chi2_contingency(table)
        sig = "**" if p < 0.01 else ("*" if p < 0.05 else "ns")
        lines.append(f"Solve rate {g1} vs {g2}: χ²={chi2:.3f}  p={p:.4f}  {sig}")

    lines.append("")
    # Turns: Mann-Whitney U
    for g1, g2 in [("A", "B"), ("A", "C"), ("B", "C")]:
        d1 = groups[g1]["num_turns"].dropna()
        d2 = groups[g2]["num_turns"].dropna()
        if d1.empty or d2.empty:
            continue
        u, p = stats.mannwhitneyu(d1, d2, alternative="two-sided")
        sig = "**" if p < 0.01 else ("*" if p < 0.05 else "ns")
        lines.append(f"Turns {g1} vs {g2}: U={u:.0f}  p={p:.4f}  {sig}")

    lines.append("\n* p<0.05  ** p<0.01  ns=not significant")

    summary = "\n".join(lines)
    print(summary)
    (FIGS_DIR / "summary.txt").write_text(summary)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    files = sorted(RESULTS_DIR.glob("group_*.jsonl"))
    if not files:
        print("No result files found in results/")
        sys.exit(1)

    print(f"Loading {len(files)} files...")
    df = load_results(files)
    print(f"Unique trials: {len(df)}  |  Groups: {df['group'].value_counts().to_dict()}\n")

    print(df.groupby("group")[["solved", "num_turns", "elapsed_call"]].agg(
        {"solved": "mean", "num_turns": ["mean", "std"], "elapsed_call": "mean"}
    ).round(2))
    print()

    plot_solve_rate(df)
    plot_turns(df)
    plot_time(df)
    plot_by_bug_type(df)
    print_summary(df)

    print(f"\nFigures saved to {FIGS_DIR}/")


if __name__ == "__main__":
    main()
