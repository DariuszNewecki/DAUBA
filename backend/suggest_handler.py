# DAUBA/backend/suggest_handler.py

"""
Handles the logic for the [[suggest:...]] directive.

Supports injecting one or more line-based code segments into the prompt,
with optional context windows for surrounding lines.
"""

import os
import re
from typing import Tuple, List

# Regex to find one or more suggest directives like [[suggest:path/to/file.py:10-20]]
SUGGEST_DIRECTIVE_PATTERN = re.compile(r"\[\[suggest:\s*(.+?)\s*\]\]", re.IGNORECASE)

# How many extra lines to include before and after the specified block
DEFAULT_CONTEXT_WINDOW = 10


def _resolve_path_safe(base_path: str, relative_path: str) -> str:
    """Safely resolve a path inside the repo, preventing path traversal."""
    base_abs = os.path.abspath(base_path)
    full_path = os.path.abspath(os.path.join(base_abs, relative_path))
    if os.path.commonpath([base_abs, full_path]) != base_abs:
        raise ValueError(f"Path traversal detected for '{relative_path}'")
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"File does not exist: '{relative_path}'")
    return full_path


def _extract_context_window(lines: List[str], start: int, end: int, window: int = DEFAULT_CONTEXT_WINDOW) -> Tuple[str, int, int]:
    """
    Extracts a slice of lines with a surrounding context window.
    Returns the extracted block and the actual line range injected.
    """
    start_idx = max(0, start - 1)
    end_idx = min(len(lines), end)

    context_start = max(0, start_idx - window)
    context_end = min(len(lines), end_idx + window)

    block = "".join(lines[context_start:context_end])
    return block, context_start + 1, context_end


def inject_suggestions(prompt: str, repo_path: str) -> Tuple[str, List[str]]:
    """
    Resolves and injects all [[suggest:...]] blocks into the prompt.

    Returns:
        (final prompt string, list of user-visible warnings)
    """
    matches = SUGGEST_DIRECTIVE_PATTERN.findall(prompt)
    if not matches:
        return prompt.strip(), []

    warnings = []
    suggestion_blocks = []

    for directive in matches:
        try:
            parts = directive.split(":")
            if len(parts) != 2:
                raise ValueError("Malformed directive — expected format: file.py:start-end")

            file_path, line_range = parts
            start_str, end_str = line_range.split("-")
            start_line = int(start_str)
            end_line = int(end_str)

            if start_line < 1 or end_line < start_line:
                raise ValueError("Invalid line range in directive.")

            resolved_path = _resolve_path_safe(repo_path, file_path)
            with open(resolved_path, "r", encoding="utf-8") as f:
                all_lines = f.readlines()

            code_block, actual_start, actual_end = _extract_context_window(all_lines, start_line, end_line)

            suggestion_blocks.append(
                "--- START SUGGEST CONTEXT ---\n"
                f"File: {file_path}\n"
                f"Lines: {actual_start}-{actual_end} (selection was {start_line}-{end_line})\n"
                "```\n"
                f"{code_block.strip()}\n"
                "```\n"
                "--- END SUGGEST CONTEXT ---"
            )

        except (ValueError, FileNotFoundError) as e:
            warnings.append(f"[[suggest:{directive}]] → {e}")
        except Exception as e:
            warnings.append(f"[[suggest:{directive}]] → Unexpected error: {e}")

    # Remove all suggest directives from the prompt
    clean_prompt = SUGGEST_DIRECTIVE_PATTERN.sub("", prompt).strip()

    if suggestion_blocks:
        injected = "\n\n".join(suggestion_blocks)
        final_prompt = f"# Suggested Context Blocks\n{injected}\n\n# User Prompt\n{clean_prompt}"
    else:
        final_prompt = clean_prompt

    return final_prompt, warnings
