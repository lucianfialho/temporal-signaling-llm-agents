"""
Creates isolated temp directories for each trial.
Claude gets: the file path, not the buggy code directly.
Must use Read/Edit/Bash tools to find and fix the bug.
This forces actual agentic iteration.
"""

import tempfile
import textwrap
from pathlib import Path


def create_trial_dir(problem: dict) -> Path:
    """
    Creates a temp dir with:
      - solution.py   : the BUGGY implementation (Claude can read this)
      - test_runner.py: runs the tests (Claude can execute this)
      - .hidden_tests : actual test assertions (Claude should NOT read this)

    Returns the temp dir path.
    """
    tmpdir = Path(tempfile.mkdtemp(prefix=f"trial_{problem['task_id'].replace('/', '_')}_"))

    # Buggy implementation — Claude reads and edits this
    buggy_code = problem["declaration"] + problem["buggy_solution"]
    (tmpdir / "solution.py").write_text(buggy_code)

    # Test runner — Claude runs this to get feedback
    entry = problem["entry_point"]
    test_runner = textwrap.dedent(f"""
        import sys
        sys.path.insert(0, '.')
        from solution import {entry}

        {problem['test']}

        try:
            check({entry})
            print("ALL TESTS PASSED")
        except AssertionError as e:
            print(f"TESTS FAILED: {{e}}")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: {{e}}")
            sys.exit(1)
    """).strip()
    (tmpdir / "test_runner.py").write_text(test_runner)

    return tmpdir


def make_agent_prompt(problem: dict, tmpdir: Path) -> str:
    return (
        f"The function `{problem['entry_point']}` in `{tmpdir}/solution.py` has a bug. "
        f"Run `python {tmpdir}/test_runner.py` to see the test results. "
        f"Fix the bug in `solution.py` so all tests pass. "
        f"When done, run the tests one final time to confirm."
    )
