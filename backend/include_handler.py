# DAUBA/backend/include_handler.py
"""
Handles the [[include:...]] directive.

Supports full file inclusion or selective function/class inclusion
based on the syntax:
  [[include:path/to/file.py]]
  [[include:path/to/file.py:function=func_name]]
"""

import os
import re
import ast
from typing import Tuple, Optional

INCLUDE_DIRECTIVE_PATTERN = re.compile(r"\[\[include:\s*(.+?)\s*\]\]", re.IGNORECASE)


def extract_function_or_class(source_code: str, name: str) -> Optional[str]:
    """Extract a function or class definition from source code."""
    try:
        tree = ast.parse(source_code)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
                return ast.get_source_segment(source_code, node)
    except SyntaxError:
        return None
    return None


def inject_includes(prompt: str, repo_path: str) -> Tuple[str, list[str]]:
    """
    Parses [[include:...]] directives and injects the referenced code
    into the prompt under an # Included: block.

    Returns:
        Tuple of (modified_prompt, warnings_list)
    """
    warnings = []
    matches = INCLUDE_DIRECTIVE_PATTERN.findall(prompt)
    clean_prompt = INCLUDE_DIRECTIVE_PATTERN.sub("", prompt).strip()

    included_blocks = []
    for raw in matches:
        path_part, _, fragment = raw.partition(":")
        file_path = path_part.strip()
        fragment = fragment.strip() if fragment else None

        abs_path = os.path.abspath(os.path.join(repo_path, file_path))
        abs_repo_path = os.path.abspath(repo_path)

        if not abs_path.startswith(abs_repo_path):
            warnings.append(f"Skipped unsafe include path: {file_path}")
            continue

        if not os.path.exists(abs_path):
            warnings.append(f"Include file not found: {file_path}")
            continue

        try:
            with open(abs_path, "r", encoding="utf-8") as f:
                content = f.read()

            if fragment.startswith("function="):
                func_name = fragment.split("=", 1)[1].strip()
                snippet = extract_function_or_class(content, func_name)
                if snippet:
                    included_blocks.append(
                        f"--- INCLUDED: {file_path} (function={func_name}) ---\n{snippet}\n--- END ---"
                    )
                else:
                    warnings.append(f"Function '{func_name}' not found in {file_path}")
            else:
                included_blocks.append(
                    f"--- INCLUDED: {file_path} ---\n{content}\n--- END ---"
                )

        except Exception as e:
            warnings.append(f"Error reading include file {file_path}: {e}")

    if not included_blocks:
        return clean_prompt, warnings

    injected_section = "\n\n".join(included_blocks)
    final_prompt = f"{injected_section}\n\n# User Request:\n{clean_prompt}"
    return final_prompt, warnings
