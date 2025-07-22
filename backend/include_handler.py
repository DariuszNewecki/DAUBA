# DAUBA/backend/include_handler.py
"""
Handles the logic for the [[include:...]] directive.

Safely resolves paths, parses include targets (functions/classes), and
injects selected blocks or full files into the prompt. Large files are
clipped to avoid overloading the LLM.
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
    """Extract a specific function or class by name from the source code."""
    try:
        tree = ast.parse(code)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
                return ast.get_source_segment(code, node)
    except Exception as e:
        return f"# Failed to extract '{name}': {e}"
    return f"# Could not find target: {name}"

def inject_includes(prompt: str, repo_path: str) -> Tuple[str, List[str]]:
    """
    Parses [[include:...]] directives and injects selected file/code blocks.

    Returns:
        Tuple[str, List[str]]: The enriched prompt and any warnings.
    """
    matches = INCLUDE_DIRECTIVE_PATTERN.findall(prompt)
    warnings = []
    included_blocks = []
    clean_prompt = INCLUDE_DIRECTIVE_PATTERN.sub("", prompt).strip()

    for raw in matches:
        file_part, target = raw.split(':', 1) if ':' in raw else (raw, None)
        file_path = file_part.strip()

        try:
            full_path = os.path.abspath(os.path.join(repo_path, file_path))
            if not full_path.startswith(os.path.abspath(repo_path)):
                warnings.append(f"Skipped unsafe include outside repo: {file_path}")
                continue

            with open(full_path, 'r', encoding='utf-8') as f:
                code = f.read()

            # --- Enforce token budget for full-file includes ---
            if not target and _estimate_token_count(code) > MAX_INCLUDE_TOKENS:
                warnings.append(f"Include skipped: '{file_path}' exceeds token limit.")
                included_blocks.append(f"# SKIPPED large include: {file_path}")
                continue

            if target:
                if '=' in target:
                    key, val = target.split('=', 1)
                    val = val.strip()
                    if key.strip() in {"function", "class"}:
                        snippet = _extract_named_function_or_class(code, val)
                        included_blocks.append(f"# Included from {file_path}:{key}={val}\n{snippet}")
                    else:
                        warnings.append(f"Unsupported target type in: {raw}")
                else:
                    warnings.append(f"Malformed include target: {raw}")
            else:
                included_blocks.append(f"# Included from {file_path}\n{code}")

        except FileNotFoundError:
            warnings.append(f"File not found: {file_path}")
        except Exception as e:
            warnings.append(f"Error reading include '{file_path}': {e}")

    if included_blocks:
        injected_block = "\n\n".join(included_blocks)
        final_prompt = f"# Included Code Blocks\n{injected_block}\n\n# User Prompt\n{clean_prompt}"
    else:
        final_prompt = clean_prompt

    return final_prompt, warnings
