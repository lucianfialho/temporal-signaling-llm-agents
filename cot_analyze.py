"""
Analyze chain-of-thought reasoning text to test H1 vs H2.

H1 (cognitive): model explicitly verbalizes the attempt signal
H2 (anchoring): model acts differently but never mentions the signal
"""

import json
import re
from pathlib import Path
import numpy as np
from scipy import stats

# Keywords suggesting explicit use of the attempt signal
SIGNAL_WORDS = [
    r"\battempt\b", r"\btries?\b", r"\bremaining\b", r"1 of \d",
    r"\d of \d", r"budget", r"limited", r"only .{0,10} left",
]

# Keywords suggesting strategy change
STRATEGY_WORDS = [
    r"different approach", r"try (?:a )?(?:different|another|new)",
    r"instead", r"alternatively", r"rather than",
    r"let me reconsider", r"step back",
]


def mentions(text: str, patterns: list[str]) -> int:
    return sum(1 for p in patterns if re.search(p, text, re.IGNORECASE))


def analyze_group(path: Path) -> list[dict]:
    results = []
    for line in open(path):
        r = json.loads(line)
        full = r.get("full_reasoning", "")
        blocks = r.get("text_blocks", [])
        results.append({
            "task_id": r["task_id"],
            "group": r["group"],
            "num_turns": r.get("num_turns", 0),
            "solved": r.get("solved", False),
            "signal_mentions": mentions(full, SIGNAL_WORDS),
            "strategy_mentions": mentions(full, STRATEGY_WORDS),
            "total_text_len": len(full),
            "n_text_blocks": len(blocks),
            "first_block": blocks[0][:200] if blocks else "",
        })
    return results


def main():
    files = {g: Path(f"results/cot_group_{g}.jsonl") for g in "ACD"}
    data = {}
    for g, f in files.items():
        if f.exists():
            data[g] = analyze_group(f)
            print(f"Group {g}: {len(data[g])} sessions loaded")

    if not data:
        print("No CoT files found. Run cot_capture.py first.")
        return

    print("\n=== SIGNAL VERBALIZATION (H1 vs H2) ===\n")
    for g, rows in data.items():
        sm = [r["signal_mentions"] for r in rows]
        st = [r["strategy_mentions"] for r in rows]
        tl = [r["total_text_len"] for r in rows]
        sr = sum(1 for r in rows if r["signal_mentions"] > 0)
        print(f"Group {g} (n={len(rows)}):")
        print(f"  Sessions with signal mention: {sr}/{len(rows)} ({sr/len(rows):.0%})")
        print(f"  Avg signal mentions/session:  {np.mean(sm):.2f}")
        print(f"  Avg strategy words/session:   {np.mean(st):.2f}")
        print(f"  Avg reasoning length:         {np.mean(tl):.0f} chars")
        print(f"  Avg turns:                    {np.mean([r['num_turns'] for r in rows]):.2f}")
        print()

    # Statistical comparison of signal mentions A vs C
    if "A" in data and "C" in data:
        a_sm = [r["signal_mentions"] for r in data["A"]]
        c_sm = [r["signal_mentions"] for r in data["C"]]
        u, p = stats.mannwhitneyu(a_sm, c_sm, alternative="two-sided")
        print(f"Signal mentions A vs C: p={p:.4f} {'*' if p<0.05 else 'ns'}")

    print("\n=== SAMPLE FIRST TEXT BLOCKS ===")
    for g, rows in data.items():
        print(f"\n--- Group {g} (first 3 examples) ---")
        for r in rows[:3]:
            print(f"  {r['task_id']}: {r['first_block'][:150]}...")


if __name__ == "__main__":
    main()
