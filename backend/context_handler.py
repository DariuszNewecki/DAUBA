# DAUBA/backend/context_handler.py
"""
Handles the logic for the [[context:...]] directive.

Parses the directive, safely loads file contents, and injects them
into the prompt before it's sent to the LLM.
"""

import os
import re
import ast
from typing import List, Tuple

# Regex to find the context directive
CONTEXT_DIRECTIVE_PATTERN = re.compile(r"\[\[context:\s*(.+?)\s*\]\]", re.IGNORECASE)

# Default token limit (can be adjusted)
MAX_CONTEXT_TOKENS = 1000


def parse_context_directive(prompt: str) -> Tuple[List[str], str]:
    """
    Extract file paths from the [[context:...]] directive and return cleaned prompt.
    """
    match = CONTEXT_DIRECTIVE_PATTERN.search(prompt)
    if not match:
        return [], prompt.strip()

    file_list_str = match.group(1)
    file_paths = [path.strip() for path in file_list_str.split(',') if path.strip()]
    clean_prompt = CONTEXT_DIRECTIVE_PATTERN.sub("", prompt).strip()
    return file_paths, clean_prompt


def resolve_path_safe(base_path: str, relative_path: str) -> str:
    """Safely resolve file path and prevent path traversal."""
    full_path = os.path.abspath(os.path.join(base_path, relative_path))
    if not full_path.startswith(os.path.abspath(base_path)):
        raise ValueError("Path traversal detected")
    return full_path


def extract_high_signal_blocks(code: str) -> str:
    """
    Extract top-level imports, function/class definitions, and docstrings using AST.
    """
    try:
        parsed = ast.parse(code)
        blocks = []

        for node in parsed.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                blocks.append(ast.get_source_segment(code, node))
            elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Str):
                # Top-level docstring
                blocks.append(ast.get_source_segment(code, node))
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                blocks.append(ast.get_source_segment(code, node))

        return "\n\n".join([b for b in blocks if b])
    except Exception:
        return code  # Fallback: return raw file


def estimate_token_count(text: str) -> int:
    """Rough token estimate based on whitespace."""
    return len(text.split())


def inject_context(prompt: str, repo_path: str, max_tokens: int = MAX_CONTEXT_TOKENS) -> Tuple[str, List[str]]:
    """
    Parses the [[context:...]] directive and injects valid file content into the prompt.

    Returns:
        Tuple[str, List[str]]: (final prompt, list of warnings)
    """
    file_paths, clean_prompt = parse_context_directive(prompt)
    context_blocks = []
    warnings = []
    token_budget = max_tokens

    for file_path in file_paths:
        try:
            resolved_path = resolve_path_safe(repo_path, file_path)
            with open(resolved_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()

            context = extract_high_signal_blocks(raw_content)
            tokens = estimate_token_count(context)

            if tokens > token_budget:
                context = f"# [TRUNCATED] Context from {file_path} exceeded token limit.\n"
                warnings.append(f"Truncated: {file_path} exceeds token budget")
                continue

            context_blocks.append(f"--- START CONTEXT FROM: {file_path} ---\n{context}\n--- END CONTEXT FROM: {file_path} ---")
            token_budget -= tokens

        except FileNotFoundError:
            warnings.append(f"File not found: {file_path}")
        except ValueError:
            warnings.append(f"Skipped unsafe file path: {file_path}")
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
