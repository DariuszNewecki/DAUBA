# DAUBA/backend/suggest_handler.py
"""
Handles the logic for the [[suggest:...]] directive.

Parses the directive, safely loads the specified file, extracts the selected
lines plus a surrounding context window, and injects this block into the prompt.
"""

import os
import re
from typing import Tuple, List

# Regex to find one or more suggest directives.
# Example: [[suggest:src/file.py:23-31]]
SUGGEST_DIRECTIVE_PATTERN = re.compile(r"\[\[suggest:\s*(.+?)\s*\]\]", re.IGNORECASE)

def _resolve_path_safe(base_path: str, relative_path: str) -> str:
    """Safely resolve file path and prevent path traversal."""
    full_path = os.path.abspath(os.path.join(base_path, relative_path))
    if not full_path.startswith(os.path.abspath(base_path)):
        raise ValueError(f"Path traversal detected for '{relative_path}'")
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"File does not exist at '{relative_path}'")
    return full_path

def _extract_context_window(lines: List[str], start: int, end: int, window: int = 10) -> Tuple[str, int, int]:
    """
    Extracts a slice of lines with a surrounding context window.
    Line numbers are 1-based and inclusive.
    """
    # Convert 1-based line numbers to 0-based list indices
    start_idx = max(0, start - 1)
    end_idx = min(len(lines), end)

    # Calculate the context window boundaries
    context_start_idx = max(0, start_idx - window)
    context_end_idx = min(len(lines), end_idx + window)

    # Extract the code block and determine the actual start/end line numbers
    code_block = "".join(lines[context_start_idx:context_end_idx])
    actual_start_line = context_start_idx + 1
    actual_end_line = context_end_idx

    return code_block, actual_start_line, actual_end_line

def inject_suggestions(prompt: str, repo_path: str) -> Tuple[str, List[str]]:
    """
    Finds all [[suggest:...]] directives, loads the specified code blocks,
    and injects them into the prompt.

    For now, only the first valid directive is processed to keep the MVP simple.
    """
    matches = SUGGEST_DIRECTIVE_PATTERN.findall(prompt)
    warnings = []

    # Per the design, only handle the first match for now.
    if not matches:
        return prompt, warnings

    target_str = matches[0]

    # Replace the directive in the prompt immediately. We will either fill this
    # space with the code block or an error message.
    clean_prompt = SUGGEST_DIRECTIVE_PATTERN.sub("{SUGGEST_BLOCK}", prompt, count=1).strip()

    injected_block = "# SUGGEST CONTEXT UNAVAILABLE: Malformed directive."

    try:
        # Parse the directive: path/to/file.py:start-end
        parts = target_str.split(':')
        if len(parts) != 2:
            raise ValueError("Malformed directive. Expected format: 'path/to/file.py:start-end'.")

        file_path, line_range = parts

        if '-' not in line_range:
            raise ValueError("Malformed line range. Expected format: 'start-end'.")

        start_line_str, end_line_str = line_range.split('-')
        start_line = int(start_line_str)
        end_line = int(end_line_str)

        if start_line > end_line or start_line < 1:
            raise ValueError("Invalid line range.")

        # Safely load the file
        resolved_path = _resolve_path_safe(repo_path, file_path)
        with open(resolved_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()

        # Extract the code with its context window
        code_block, actual_start, actual_end = _extract_context_window(all_lines, start_line, end_line)

        injected_block = (
            "--- START SUGGEST CONTEXT ---\n"
            f"File: {file_path}\n"
            f"Lines: {actual_start}-{actual_end} (selection was {start_line}-{end_line})\n"
            "```\n"
            f"{code_block.strip()}\n"
            "```\n"
            "--- END SUGGEST CONTEXT ---"
        )

    except (ValueError, FileNotFoundError) as e:
        injected_block = f"# SUGGEST CONTEXT UNAVAILABLE: {e}"
        warnings.append(str(e))
    except Exception as e:
        injected_block = f"# SUGGEST CONTEXT UNAVAILABLE: An unexpected error occurred."
        warnings.append(f"Error processing suggest directive '{target_str}': {e}")

    # Replace the placeholder with the final block (either code or error message)
    final_prompt = clean_prompt.replace("{SUGGEST_BLOCK}", injected_block)

    return final_prompt, warnings
