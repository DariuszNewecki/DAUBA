# backend/inject_analysis.py

"""
Handles the [[analyze:...]] directive in prompts.

For each requested file, runs quality analysis and generates
structured suggestions. Injects them into the prompt for LLM review.
"""

import os
import re
from typing import Tuple, List
from quality_analyzer import CodeQualityAnalyzer
from suggestion_engine import suggest_fixes

ANALYZE_DIRECTIVE_PATTERN = re.compile(r"\[\[analyze:\s*(.+?)\s*\]\]", re.IGNORECASE)


def inject_analysis(prompt: str, repo_path: str) -> Tuple[str, List[str]]:
    """
    Finds all [[analyze:...]] blocks, analyzes the code, and injects findings.

    Returns:
        (final_prompt, list_of_user_warnings)
    """
    matches = ANALYZE_DIRECTIVE_PATTERN.findall(prompt)
    if not matches:
        return prompt.strip(), []

    warnings = []
    injected_blocks = []

    # Remove directives from prompt
    cleaned_prompt = ANALYZE_DIRECTIVE_PATTERN.sub("", prompt).strip()

    analyzer = CodeQualityAnalyzer()

    for relative_path in matches:
        try:
            full_path = _resolve_path_safe(repo_path, relative_path)
            issues = analyzer.analyze_file(full_path)
            suggestions = suggest_fixes(issues)

            if not suggestions:
                injected_blocks.append(
                    f"# ✅ No structural issues found in {relative_path}.\n"
                )
                continue

            injected_blocks.append(f"# 📎 Analysis Report: {relative_path}\n")

            for item in suggestions:
                injected_blocks.append(format_suggestion(item))

        except Exception as e:
            warnings.append(f"Could not analyze {relative_path}: {e}")

    final_block = "\n\n".join(injected_blocks)
    final_prompt = (
        "The user requested structural analysis of the following file(s).\n"
        "Please review the issues and suggestions below, and act accordingly.\n\n"
        f"{final_block}\n\n# User Prompt\n{cleaned_prompt}"
    )

    return final_prompt, warnings


def _resolve_path_safe(base_path: str, relative_path: str) -> str:
    base_abs = os.path.abspath(base_path)
    full_path = os.path.abspath(os.path.join(base_abs, relative_path))
    if os.path.commonpath([base_abs, full_path]) != base_abs:
        raise ValueError(f"Path traversal blocked for: {relative_path}")
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"File does not exist: {relative_path}")
    return full_path


def format_suggestion(item: dict) -> str:
    file = item.get("location", {}).get("file", "unknown")
    line = item.get("location", {}).get("line", "?")
    msg = item.get("message", "No message")
    fix = item.get("suggestion", "")
    steps = item.get("refactor_plan", [])
    severity = item.get("severity", "moderate")

    steps_text = "\n".join(f"  - {s}" for s in steps)
    return (
        f"## 🔧 {msg} (Line {line}, Severity: {severity})\n"
        f"Suggested fix: {fix}\n"
        f"Refactor plan:\n{steps_text}\n"
    )
