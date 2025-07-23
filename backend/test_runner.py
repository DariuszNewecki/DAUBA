# DAUBA/backend/test_runner.py

"""
Runs pytest against the local /tests directory and captures results.

Used to verify correctness after a file write, or to power future test dashboards.
Also logs test results to logs/test_results.log with timestamp.
"""

import subprocess
import os
import json
import datetime
from typing import Dict

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "test_results.log")
os.makedirs(LOG_DIR, exist_ok=True)

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
            "timestamp": str (UTC ISO format),
        }
    """
    result = {
        "exit_code": "-1",
        "stdout": "",
        "stderr": "",
        "summary": "❌ Unknown error",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    tests_path = os.path.join(repo_root, "tests")
    cmd = ["pytest", tests_path, "--tb=short", "-q"]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        result["exit_code"] = str(proc.returncode)
        result["stdout"] = proc.stdout.strip()
        result["stderr"] = proc.stderr.strip()
        result["summary"] = _summarize(proc.stdout)

        if not silent:
            print(proc.stdout)
            if proc.stderr:
                print("⚠️ stderr:", proc.stderr)

    except FileNotFoundError:
        result["stderr"] = "pytest is not installed or not found in PATH."
        result["summary"] = "❌ Pytest not available"
    except Exception as e:
        result["stderr"] = str(e)
        result["summary"] = "❌ Test run error"

    _log_test_result(result)
    return result


def _summarize(output: str) -> str:
    """
    Extracts last line from pytest output for quick summary.
    """
    lines = output.strip().splitlines()
    for line in reversed(lines):
        if "passed" in line or "failed" in line or "error" in line:
            return line.strip()
    return "No test summary found."


def _log_test_result(data: Dict[str, str]):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")
    except Exception as e:
        print(f"Warning: Failed to write test log: {e}")