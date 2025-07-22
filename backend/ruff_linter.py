# DAUBA/backend/ruff_linter.py

"""
Runs Ruff lint checks on generated Python code before it's staged.

Returns a success flag and an optional linting message.
"""

import subprocess
import tempfile
import os
from typing import Tuple


def lint_code_with_ruff(code: str, display_filename: str = "<code>") -> Tuple[bool, str]:
    """
    Lint the provided Python code using Ruff.

    Args:
        code (str): Source code to lint.
        display_filename (str): Optional display name (e.g., intended file path).

    Returns:
        (is_clean: bool, message: str)
    """
    tmp_file_path = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as tmp_file:
            tmp_file.write(code)
            tmp_file_path = tmp_file.name

        result = subprocess.run(
            ["ruff", tmp_file_path, "--quiet"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode == 0:
            return True, ""

        # Replace temp path in output with the expected file path for user readability
        readable_output = result.stdout.replace(tmp_file_path, display_filename)
        return False, readable_output.strip()

    except FileNotFoundError:
        return False, "Ruff is not installed or not in your PATH. Please install it to enable lint checks."

    except Exception as e:
        return False, f"Ruff execution failed: {e}"

    finally:
        if tmp_file_path and os.path.exists(tmp_file_path):
            try:
                os.remove(tmp_file_path)
            except Exception:
                pass  # Don't crash if temp cleanup fails
