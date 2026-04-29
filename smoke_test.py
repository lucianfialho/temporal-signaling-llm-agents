"""
Smoke test: roda 3 problemas por grupo pra confirmar que tudo funciona
antes de rodar o experimento completo.
"""

import subprocess
import sys
from datasets import load_dataset

def test_runner():
    ds = load_dataset("openai/openai_humaneval", split="test")
    problem = list(ds)[0]
    print(f"Test problem: {problem['task_id']}")
    print(f"  Entry point: {problem['entry_point']}")
    print(f"  Prompt snippet: {problem['prompt'][:80]}...")

    # Test the claude call
    print("\nTesting claude -p (bare mode, 1 attempt)...")
    result = subprocess.run(
        ["claude", "-p",
         f"Implement this Python function. Return ONLY the function in a ```python``` block.\n\n{problem['prompt']}",
         "--output-format", "json",
         "--allowedTools", "Bash"],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        print(f"ERROR: {result.stderr[:300]}")
        sys.exit(1)

    import json
    data = json.loads(result.stdout)
    print(f"  Session ID: {data.get('session_id', 'N/A')}")
    print(f"  Response length: {len(data.get('result', ''))} chars")
    print(f"  First 200 chars: {data.get('result', '')[:200]}")
    print("\n✓ Claude call works")

    # Test code extraction + test runner
    from runner import extract_code, run_tests
    code = extract_code(data.get("result", ""))
    print(f"\nExtracted code ({len(code)} chars):")
    print(code[:300])

    solved, err = run_tests(code, problem["test"], problem["entry_point"])
    print(f"\nTest result: {'✓ SOLVED' if solved else f'✗ failed — {err[:200]}'}")

if __name__ == "__main__":
    test_runner()
