"""
Injects deterministic bugs into HumanEval canonical solutions.
Goal: guarantee attempt 1 fails so we can measure retry behavior.
"""

import ast
import random
import re


MUTATIONS = [
    # Off-by-one
    ("+ 1", "+ 2"),
    ("- 1", "- 2"),
    ("<", "<="),
    (">", ">="),
    ("<=", "<"),
    (">=", ">"),
    # Logic flips
    ("and", "or"),
    ("or", "and"),
    ("not ", ""),
    # Wrong return
    ("return True", "return False"),
    ("return False", "return True"),
    # Wrong operator
    (" + ", " - "),
    (" * ", " + "),
    (" // ", " / "),
    (" % ", " // "),
]


def full_function(problem: dict) -> str:
    """Combine prompt (signature+docstring) with canonical body."""
    return problem["prompt"] + problem["canonical_solution"]


def inject_bug(code: str, seed: int = 42) -> tuple[str, str]:
    """
    Try mutations in random order; return first that syntactically applies.
    Does NOT guarantee test failure — use find_effective_bug for that.
    """
    rng = random.Random(seed)
    lines = code.splitlines()
    muts = MUTATIONS[:]
    rng.shuffle(muts)

    for old, new in muts:
        candidates = [(i, l) for i, l in enumerate(lines) if old in l]
        if not candidates:
            continue
        i, line = rng.choice(candidates)
        buggy_lines = lines[:]
        buggy_lines[i] = line.replace(old, new, 1)
        buggy = "\n".join(buggy_lines)
        return buggy, f"'{old}' → '{new}' on line {i+1}"

    return code, "no mutation found"


def find_effective_multi_bug(problem: dict, run_tests_fn, n_bugs: int = 2) -> tuple[str, str] | None:
    """
    Inject n_bugs independent mutations that together cause test failure.
    Returns (buggy_code, description) or None.
    """
    complete = full_function(problem)
    entry    = problem["entry_point"]
    tests    = problem["test"]
    lines    = complete.splitlines()

    rng  = random.Random(hash(problem["task_id"]) % 10000)
    muts = MUTATIONS[:]
    rng.shuffle(muts)

    # Find all applicable mutations
    applicable = []
    for old, new in muts:
        for i, line in enumerate(lines):
            if old in line:
                applicable.append((i, line, old, new))

    if len(applicable) < n_bugs:
        return None

    # Try combinations of n_bugs mutations
    rng.shuffle(applicable)
    from itertools import combinations
    for combo in list(combinations(applicable, n_bugs))[:50]:
        # Check mutations are on different lines
        lines_used = [c[0] for c in combo]
        if len(set(lines_used)) < n_bugs:
            continue

        buggy_lines = lines[:]
        descs = []
        for idx, line, old, new in combo:
            buggy_lines[idx] = buggy_lines[idx].replace(old, new, 1)
            descs.append(f"'{old}'→'{new}' L{idx+1}")

        buggy = "\n".join(buggy_lines)
        passed, _ = run_tests_fn(buggy, tests, entry)
        if not passed:
            return buggy, " | ".join(descs)

    return None


def find_effective_bug(problem: dict, run_tests_fn) -> tuple[str, str] | None:
    """
    Try every mutation until one that actually makes the tests fail.
    Returns (buggy_code, description) or None if no effective mutation found.
    """
    complete = full_function(problem)
    entry    = problem["entry_point"]
    tests    = problem["test"]
    lines    = complete.splitlines()

    rng = random.Random(hash(problem["task_id"]) % 10000)
    muts = MUTATIONS[:]
    rng.shuffle(muts)

    for old, new in muts:
        candidates = [(i, l) for i, l in enumerate(lines) if old in l]
        if not candidates:
            continue
        for idx, line in candidates:
            buggy_lines = lines[:]
            buggy_lines[idx] = line.replace(old, new, 1)
            buggy = "\n".join(buggy_lines)
            passed, _ = run_tests_fn(buggy, tests, entry)
            if not passed:
                return buggy, f"'{old}' → '{new}' on line {idx+1}"

    return None


def make_debug_prompt(problem: dict, run_tests_fn) -> tuple[str, str, str] | None:
    """Returns (prompt, buggy_code, bug_desc) or None if no effective bug found."""
    # Try multi-bug first (harder), fall back to single bug
    result = find_effective_multi_bug(problem, run_tests_fn, n_bugs=2)
    if result is None:
        result = find_effective_bug(problem, run_tests_fn)
    if result is None:
        return None
    buggy, desc = result
    prompt = (
        f"The following Python function has a bug — it fails the test suite. "
        f"Find and fix the bug. Return ONLY the corrected function in a ```python``` block.\n\n"
        f"```python\n{buggy}\n```"
    )
    return prompt, buggy, desc
