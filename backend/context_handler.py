# DAUBA/backend/context_handler.py

"""
Handles the logic for the [[context:...]] directive.

Supports injecting multiple file references into the LLM prompt, with
AST-based clipping for large files and strong path security checks.
"""

import os
import re
import ast
from typing import List, Tuple

# Regex pattern to find all [[context: file1.py, file2.py]] blocks
CONTEXT_DIRECTIVE_PATTERN = re.compile(r"\[\[context:\s*(.+?)\s*\]\]", re.IGNORECASE)

# Token budget settings
MAX_CONTEXT_TOKENS = 1000
MAX_TOKENS_PER_FILE = 500


def parse_context_directive(prompt: str) -> Tuple[List[str], str]:
    """
    Extracts all file paths from one or more [[context:...]] directives.

    Returns:
        (list of file paths, cleaned prompt with directives removed)
    """
    matches = CONTEXT_DIRECTIVE_PATTERN.findall(prompt)
    if not matches:
        return [], prompt.strip()

    all_paths = []
    for file_list_str in matches:
        paths = [p.strip() for p in file_list_str.split(",") if p.strip()]
        all_paths.extend(paths)

    clean_prompt = CONTEXT_DIRECTIVE_PATTERN.sub("", prompt).strip()
    return all_paths, clean_prompt


def resolve_path_safe(base_path: str, relative_path: str) -> str:
    """
    Resolves a relative path safely inside the given base path.

    Raises ValueError if path escapes the base.
    """
    base_abs = os.path.abspath(base_path)
    full_path = os.path.abspath(os.path.join(base_abs, relative_path))

    if os.path.commonpath([base_abs, full_path]) != base_abs:
        raise ValueError(f"Path traversal detected for '{relative_path}'")

    return full_path


def extract_high_signal_blocks(code: str) -> str:
    """
    Uses AST to extract high-signal elements from code:
    - Imports
    - Function and class headers
    - Docstrings
    """
    try:
        parsed = ast.parse(code)
        blocks = []

        for node in parsed.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                blocks.append(ast.get_source_segment(code, node))

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                header = f"\n# --- {node.__class__.__name__}: {node.name} ---\n"
                docstring = ast.get_docstring(node)
                doc_block = f'"""{docstring}"""' if docstring else ""
                blocks.append(f"{header}{doc_block}\n# ... clipped ...")

            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                blocks.append(ast.get_source_segment(code, node))

        return "\n\n".join([b for b in blocks if b])
    except Exception:
        return "# WARNING: Failed to parse file with AST. Injecting raw content.\n" + code


def estimate_token_count(text: str) -> int:
    """
    Rough word-based token estimate.
    """
    return len(text.split())


def inject_context(prompt: str, repo_path: str, max_tokens: int = MAX_CONTEXT_TOKENS) -> Tuple[str, List[str]]:
    """
    Resolves and injects content from all referenced context files into the prompt.

    Returns:
        (final enriched prompt, list of user-facing warnings)
    """
    file_paths, clean_prompt = parse_context_directive(prompt)
    context_blocks = []
    warnings = []
    token_budget = max_tokens

    for file_path in file_paths:
        try:
            resolved_path = resolve_path_safe(repo_path, file_path)
            with open(resolved_path, "r", encoding="utf-8") as f:
                raw_content = f.read()

            estimated_full = estimate_token_count(raw_content)

            if estimated_full <= MAX_TOKENS_PER_FILE:
                content = raw_content
                clipped = False
            else:
                content = extract_high_signal_blocks(raw_content)
                clipped = True

            tokens = estimate_token_count(content)

            if tokens > token_budget:
                warnings.append(f"Skipping {file_path}: not enough token budget ({token_budget} left, needed {tokens})")
                continue

            header = f"--- START CONTEXT FROM: {file_path} ---\n"
            if clipped:
                header += "# NOTE: File was too large. Injected high-signal content only.\n"
                warnings.append(f"Clipped {file_path} to fit token budget")

            context_blocks.append(f"{header}{content}\n--- END CONTEXT FROM: {file_path} ---")
            token_budget -= tokens

        except FileNotFoundError:
            warnings.append(f"File not found: {file_path}")
        except ValueError as ve:
            warnings.append(str(ve))
        except Exception as e:
            warnings.append(f"Error reading {file_path}: {e}")

    if not context_blocks:
        return clean_prompt, warnings

    injected_context = "\n\n".join(context_blocks)
    final_prompt = (
        "Based on the following file context, please answer the user's request.\n\n"
        f"{injected_context}\n\n"
        "--- USER REQUEST ---\n"
        f"{clean_prompt}"
    )
    return final_prompt, warnings
