# DAUBA/backend/include_handler.py

"""
Handles the logic for the [[include:...]] directive.

Safely resolves paths, parses include targets (functions/classes), and
injects selected blocks or full files into the prompt.
"""

import os
import re
import ast
from typing import List, Tuple

INCLUDE_DIRECTIVE_PATTERN = re.compile(r"\[\[include:(.+?)\]\]", re.IGNORECASE)
MAX_INCLUDE_TOKENS = 2000


def _estimate_token_count(text: str) -> int:
    """Rough token estimate based on word count."""
    return len(text.split())


def _extract_named_function_or_class(code: str, name: str) -> str:
    """Extract a specific top-level function or class from the source code."""
    try:
        tree = ast.parse(code)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
                return ast.get_source_segment(code, node)
    except Exception as e:
        return f"# Failed to extract '{name}': {e}"
    return f"# Could not find target: {name}"


def _resolve_path_safe(base_path: str, relative_path: str) -> str:
    """Resolves a path inside the base directory securely."""
    base_abs = os.path.abspath(base_path)
    full_path = os.path.abspath(os.path.join(base_abs, relative_path))
    if os.path.commonpath([base_abs, full_path]) != base_abs:
        raise ValueError(f"Path traversal detected: {relative_path}")
    return full_path


def inject_includes(prompt: str, repo_path: str) -> Tuple[str, List[str]]:
    """
    Parses [[include:...]] directives and injects the requested file/code blocks.

    Returns:
        (str: enriched prompt, list of warning messages)
    """
    matches = INCLUDE_DIRECTIVE_PATTERN.findall(prompt)
    warnings = []
    included_blocks = []

    # Clean prompt of all include directives
    clean_prompt = INCLUDE_DIRECTIVE_PATTERN.sub("", prompt).strip()

    for raw in matches:
        file_part, target = raw.split(":", 1) if ":" in raw else (raw, None)
        file_path = file_part.strip()

        try:
            full_path = _resolve_path_safe(repo_path, file_path)
            with open(full_path, "r", encoding="utf-8") as f:
                code = f.read()

            if not target:
                token_estimate = _estimate_token_count(code)
                if token_estimate > MAX_INCLUDE_TOKENS:
                    warnings.append(f"Include skipped: '{file_path}' exceeds token limit.")
                    included_blocks.append(f"# SKIPPED large include: {file_path}")
                else:
                    included_blocks.append(f"# Included from {file_path}\n{code}")
                continue

            # Parse target
            if "=" in target:
                key, val = target.split("=", 1)
                val = val.strip()
                key = key.strip().lower()

                if key in {"function", "class"}:
                    snippet = _extract_named_function_or_class(code, val)
                    included_blocks.append(f"# Included from {file_path}:{key}={val}\n{snippet}")
                else:
                    warnings.append(f"Unsupported include type: {key} in {raw}")
            else:
                warnings.append(f"Malformed include target: {raw}")

        except FileNotFoundError:
            warnings.append(f"File not found: {file_path}")
        except ValueError as ve:
            warnings.append(str(ve))
        except Exception as e:
            warnings.append(f"Error reading include '{file_path}': {e}")

    if included_blocks:
        injected_block = "\n\n".join(included_blocks)
        final_prompt = f"# Included Code Blocks\n{injected_block}\n\n# User Prompt\n{clean_prompt}"
    else:
        final_prompt = clean_prompt

    return final_prompt, warnings
