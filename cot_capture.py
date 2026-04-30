"""
Capture chain-of-thought reasoning text from Claude Code sessions.
Runs groups A, C, D and extracts all TEXT events from stream-JSON output.
"""

import subprocess
import json
import time
import sys
from pathlib import Path
from datasets import load_dataset
from trial_setup import create_trial_dir, make_agent_prompt
import shutil

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)
MAX_ATTEMPTS = 5

SIGNAL = {
    "A": None,
    "C": "[attempt: 1/{max}]",
    "D": None,
}
SYSTEM = {
    "A": None,
    "C": "You are a debugging assistant. You will be told how many attempts you've made. If previous attempts failed, try a different approach.",
    "D": "You are a debugging assistant. As you work, if you're not making progress, try a fundamentally different approach.",
}


def capture_session(problem: dict, group: str) -> dict:
    tmpdir = create_trial_dir(problem)
    base_prompt = make_agent_prompt(problem, tmpdir)

    prefix = SIGNAL.get(group, "")
    if prefix:
        prefix = prefix.format(max=MAX_ATTEMPTS)
        prompt = f"{prefix}\n\n{base_prompt}"
    else:
        prompt = base_prompt

    cmd = [
        "claude", "-p", prompt,
        "--output-format", "stream-json",
        "--verbose",
        "--allowedTools", "Bash,Read,Edit",
        "--model", "sonnet",
    ]
    if SYSTEM.get(group):
        cmd += ["--append-system-prompt", SYSTEM[group]]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        raw = proc.stdout
    except subprocess.TimeoutExpired:
        shutil.rmtree(tmpdir, ignore_errors=True)
        return {"task_id": problem["task_id"], "group": group, "error": "timeout"}

    # Parse stream events
    text_blocks = []
    tool_uses = []
    num_turns = 0
    solved = False

    for line in raw.splitlines():
        if not line.strip():
            continue
        try:
            e = json.loads(line)
        except:
            continue

        t = e.get("type", "")
        if t == "assistant":
            content = e.get("message", {}).get("content", [])
            for c in content:
                if c.get("type") == "text":
                    text_blocks.append(c.get("text", "").strip())
                elif c.get("type") == "tool_use":
                    tool_uses.append({"name": c.get("name"), "input": c.get("input", {})})
        elif t == "result":
            num_turns = e.get("num_turns", 0)
            solved = not e.get("is_error", False)

    shutil.rmtree(tmpdir, ignore_errors=True)

    return {
        "task_id": problem["task_id"],
        "group": group,
        "num_turns": num_turns,
        "solved": solved,
        "text_blocks": text_blocks,
        "tool_uses": [t["name"] for t in tool_uses],
        "full_reasoning": "\n---\n".join(text_blocks),
    }


def main():
    group = sys.argv[1] if len(sys.argv) > 1 else "A"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 15

    ds = load_dataset("bigcode/humanevalpack", "python", split="test")
    problems = list(ds)[:n]

    out = RESULTS_DIR / f"cot_group_{group}.jsonl"
    done = set()
    if out.exists():
        done = {json.loads(l)["task_id"] for l in open(out)}

    print(f"CoT capture — Group {group} | {n} problems | {len(done)} already done\n")

    with open(out, "a") as f:
        for p in problems:
            if p["task_id"] in done:
                print(f"  skip {p['task_id']}")
                continue
            print(f"  [{group}] {p['task_id']}...", end=" ", flush=True)
            result = capture_session(p, group)
            n_text = len(result.get("text_blocks", []))
            print(f"turns={result.get('num_turns')}  texts={n_text}  solved={result.get('solved')}")
            f.write(json.dumps(result) + "\n")
            f.flush()
            time.sleep(8)

    print(f"\nDone → {out}")


if __name__ == "__main__":
    main()
