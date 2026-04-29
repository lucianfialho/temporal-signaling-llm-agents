"""
Experiment: Does elapsed time injection improve LLM problem-solving?

Groups:
  A - Control: no temporal signal
  B - Treatment: elapsed time + attempt count
  C - Ablation: attempt count only (no time)
"""

import subprocess
import json
import time
import re
import sys
import shutil
import textwrap
from datetime import datetime
from pathlib import Path
from trial_setup import create_trial_dir, make_agent_prompt

# ── Config ────────────────────────────────────────────────────────────────────
MAX_ATTEMPTS = 5
TIMEOUT_PER_CALL = 120   # seconds per claude call
RESULTS_DIR = Path("results")
LOGS_DIR    = Path("logs")

RETRY_PROMPTS = {
    "A": "The tests failed. Try again with a different approach.",
    "B": "[elapsed: {elapsed}s | attempt: {attempt}/{max}] The tests failed. Try again with a different approach.",
    "C": "[attempt: {attempt}/{max}] The tests failed. Try again with a different approach.",
}

# ── Claude call ───────────────────────────────────────────────────────────────
def call_claude(prompt: str, session_id: str | None = None) -> dict:
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--allowedTools", "Bash",
    ]
    if session_id:
        cmd += ["--resume", session_id]

    start = time.time()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_PER_CALL,
        )
        elapsed = time.time() - start
        if proc.returncode != 0:
            return {"error": proc.stderr, "elapsed_call": elapsed}
        return {**json.loads(proc.stdout), "elapsed_call": elapsed}
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "elapsed_call": TIMEOUT_PER_CALL}
    except Exception as e:
        return {"error": str(e), "elapsed_call": time.time() - start}


# ── Code extraction ───────────────────────────────────────────────────────────
def extract_code(response_text: str) -> str:
    blocks = re.findall(r"```(?:python)?\n(.*?)```", response_text, re.DOTALL)
    if blocks:
        return blocks[-1].strip()
    # fallback: grab lines that look like code (def / return / indent)
    lines = [l for l in response_text.splitlines()
             if l.startswith(("def ", "    ", "\t", "class ", "import ", "return "))]
    return "\n".join(lines).strip() if lines else response_text.strip()


# ── Test runner ───────────────────────────────────────────────────────────────
def run_tests(code: str, test_block: str, entry_point: str) -> tuple[bool, str]:
    """Execute code + tests in a subprocess. Returns (passed, error_msg)."""
    full = textwrap.dedent(f"""
{code}

{test_block}

check({entry_point})
""")
    try:
        result = subprocess.run(
            [sys.executable, "-c", full],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return True, ""
        return False, (result.stderr or result.stdout)[:400]
    except subprocess.TimeoutExpired:
        return False, "execution timeout"
    except Exception as e:
        return False, str(e)


# ── Single trial (agentic mode) ───────────────────────────────────────────────
def run_trial(problem: dict, group: str, problem_idx: int, run_id: int = 1, model: str = "sonnet") -> dict:
    task_id  = problem["task_id"]
    tests    = problem["test"]
    entry    = problem["entry_point"]
    bug_desc = problem.get("bug_type", "unknown")

    # Create isolated dir with buggy file + test runner
    tmpdir = create_trial_dir(problem)
    trial_start = time.time()

    # Build system prompt addition based on group
    if group == "A":
        system_add = None
    elif group == "B":
        system_add = (
            "You are a debugging assistant. As you work, you will be told how much time "
            "has elapsed and how many attempts you've made. Use this information to adapt "
            "your debugging strategy — if you've been working a long time without success, "
            "try a fundamentally different approach."
        )
    elif group == "C":
        system_add = (
            "You are a debugging assistant. You will be told how many attempts you've made. "
            "If previous attempts failed, try a different approach."
        )

    # Inject temporal context into the prompt for groups B and C
    elapsed = int(time.time() - trial_start)
    base_prompt = make_agent_prompt(problem, tmpdir)

    if group == "B":
        prompt = f"[session_elapsed: {elapsed}s | attempt: 1/{MAX_ATTEMPTS}]\n\n{base_prompt}"
    elif group == "C":
        prompt = f"[attempt: 1/{MAX_ATTEMPTS}]\n\n{base_prompt}"
    else:
        prompt = base_prompt

    print(f"  [{group}] {task_id} (agent run)...", flush=True)

    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--allowedTools", "Bash,Read,Edit",
        "--model", model,
    ]
    if system_add:
        cmd += ["--append-system-prompt", system_add]

    start_call = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT_PER_CALL)
        elapsed_call = time.time() - start_call
        if proc.returncode != 0:
            response = {"error": proc.stderr[:400], "elapsed_call": elapsed_call}
        else:
            response = {**json.loads(proc.stdout), "elapsed_call": elapsed_call}
    except subprocess.TimeoutExpired:
        response = {"error": "timeout", "elapsed_call": TIMEOUT_PER_CALL}

    # Check result by running tests on the (possibly edited) solution.py
    solution_path = tmpdir / "solution.py"
    final_code = solution_path.read_text() if solution_path.exists() else ""
    solved, test_err = run_tests(final_code, tests, entry)

    print(f"    → {'✓ SOLVED' if solved else '✗ failed'} "
          f"({response.get('elapsed_call', 0):.0f}s)", flush=True)

    # Capture num_turns from response (how many internal tool-use turns)
    num_turns = response.get("num_turns", 1)

    # Cleanup
    shutil.rmtree(tmpdir, ignore_errors=True)

    return {
        "task_id":      task_id,
        "group":        group,
        "run_id":       run_id,
        "model":        model,
        "problem_idx":  problem_idx,
        "bug_desc":     bug_desc,
        "solved":       solved,
        "num_turns":    num_turns,
        "elapsed_call": response.get("elapsed_call", 0),
        "total_time":   int(time.time() - trial_start),
        "test_error":   test_err,
        "response_raw": response.get("result", "")[:500],
        "error":        response.get("error"),
    }


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    import argparse
    from datasets import load_dataset

    parser = argparse.ArgumentParser()
    parser.add_argument("--group", choices=["A", "B", "C"], required=True)
    parser.add_argument("--n", type=int, default=50, help="Number of problems")
    parser.add_argument("--offset", type=int, default=0, help="Problem offset")
    parser.add_argument("--run-id", type=int, default=1, help="Replication run ID")
    parser.add_argument("--model", type=str, default="sonnet", help="Model alias: sonnet, opus, haiku")
    parser.add_argument("--resume", type=str, default=None, help="Resume from results file")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    ds = load_dataset("bigcode/humanevalpack", "python", split="test")
    problems = list(ds)[args.offset : args.offset + args.n]

    out_file = RESULTS_DIR / f"run{args.run_id}_{args.model}_group_{args.group}_{datetime.now():%Y%m%d_%H%M%S}.jsonl"

    # Resume: skip already completed tasks
    done_ids = set()
    if args.resume and Path(args.resume).exists():
        out_file = Path(args.resume)
        with open(out_file) as f:
            for line in f:
                r = json.loads(line)
                if r.get("solved"):
                    done_ids.add(r["task_id"])
        print(f"Resuming {out_file} — {len(done_ids)} already done")

    print(f"Group {args.group} | {len(problems)} problems | output → {out_file}\n")

    with open(out_file, "a") as f:
        for i, problem in enumerate(problems):
            if problem["task_id"] in done_ids:
                print(f"  skip {problem['task_id']} (already done)")
                continue

            result = run_trial(problem, args.group, args.offset + i, run_id=args.run_id, model=args.model)
            if result is None:
                continue
            f.write(json.dumps(result) + "\n")
            f.flush()
            delay = 30 if args.model == "opus" else 8
            time.sleep(delay)  # avoid subscription rate limit between calls

    print(f"\nDone. Results in {out_file}")


if __name__ == "__main__":
    main()
