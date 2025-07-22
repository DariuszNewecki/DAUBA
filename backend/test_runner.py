# DAUBA/backend/test_runner.py

"""
Runs pytest against the local /tests directory and captures results.

Used to verify correctness after a file write, or to power future test dashboards.
"""

import subprocess
import os
from typing import Dict


def run_tests(silent: bool = True) -> Dict[str, str]:
    """
    Executes pytest on the tests/ directory.

    Args:
        silent (bool): If True, suppresses test output to console.

    Returns:
        dict: {
            "exit_code": str (0 = all passed, 1+ = failure),
            "stdout": str,
            "stderr": str,
            "summary": str (short outcome),
        }
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    tests_path = os.path.join(repo_root, "tests")
    cmd = ["pytest", tests_path, "--tb=short", "-q"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        summary = _summarize(result.stdout)
        if not silent:
            print(result.stdout)
            if result.stderr:
                print("⚠️ stderr:", result.stderr)

        return {
            "exit_code": str(result.returncode),
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "summary": summary,
        }

    except FileNotFoundError:
        return {
            "exit_code": "-1",
            "stdout": "",
            "stderr": "pytest is not installed or not found in PATH.",
            "summary": "❌ Pytest not available"
        }

    except Exception as e:
        return {
            "exit_code": "-1",
            "stdout": "",
            "stderr": str(e),
            "summary": "❌ Test run error"
        }


def _summarize(output: str) -> str:
    """
    Extracts last line from pytest output for quick summary.
    """
    lines = output.strip().splitlines()
    for line in reversed(lines):
        if "passed" in line or "failed" in line or "error" in line:
            return line.strip()
    return "No test summary found."