# backend/quality_analyzer.py

import ast
import os
from typing import Any, List, Optional

BAD_NAME_PATTERNS = {"foo", "bar", "temp", "data", "test", "x", "y", "z"}
MAX_FUNCTION_LENGTH = 50
MAX_TOP_LEVEL_STATEMENTS = 10


class CodeQualityAnalyzer:
    def __init__(self, manifest: Optional[dict] = None):
        self.manifest = manifest or {}

        # Override defaults if manifest specifies rules
        self.bad_names = set(self.manifest.get("bad_names", BAD_NAME_PATTERNS))
        self.max_func_length = self.manifest.get("max_function_length", MAX_FUNCTION_LENGTH)
        self.max_statements = self.manifest.get("max_top_level_statements", MAX_TOP_LEVEL_STATEMENTS)

    def analyze_file(self, path: str) -> List[dict[str, Any]]:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        return self.analyze_code(code, path_hint=path)

    def analyze_code(self, code: str, path_hint: str = "") -> List[dict[str, Any]]:
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [{
                "type": "syntax_error",
                "message": f"Syntax error in file: {e}",
                "severity": "critical",
                "location": {"file": path_hint, "line": e.lineno or 0},
                "target": None,
            }]

        issues = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                issues.extend(self._analyze_function(node, path_hint))
            elif isinstance(node, ast.ClassDef):
                issues.extend(self._analyze_class(node, path_hint))
        return issues

    def _analyze_function(self, node: ast.FunctionDef, file_path: str) -> List[dict[str, Any]]:
        issues = []

        # Missing docstring
        if not ast.get_docstring(node):
            issues.append({
                "type": "missing_docstring",
                "message": f"Function '{node.name}' is missing a docstring.",
                "severity": "moderate",
                "location": {"file": file_path, "line": node.lineno},
                "target": node.name,
            })

        # Bad naming
        if node.name in self.bad_names:
            issues.append({
                "type": "bad_naming",
                "message": f"Function '{node.name}' uses a weak or generic name.",
                "severity": "minor",
                "location": {"file": file_path, "line": node.lineno},
                "target": node.name,
            })

        # Too many top-level statements
        if len(node.body) > self.max_statements:
            issues.append({
                "type": "low_cohesion",
                "message": f"Function '{node.name}' has too many top-level statements ({len(node.body)}).",
                "severity": "moderate",
                "location": {"file": file_path, "line": node.lineno},
                "target": node.name,
            })

        # Too many lines
        if hasattr(node, "end_lineno"):
            func_length = node.end_lineno - node.lineno
            if func_length > self.max_func_length:
                issues.append({
                    "type": "too_long",
                    "message": f"Function '{node.name}' is too long ({func_length} lines).",
                    "severity": "moderate",
                    "location": {"file": file_path, "line": node.lineno},
                    "target": node.name,
                })

        return issues

    def _analyze_class(self, node: ast.ClassDef, file_path: str) -> List[dict[str, Any]]:
        issues = []

        # Missing class docstring
        if not ast.get_docstring(node):
            issues.append({
                "type": "missing_docstring",
                "message": f"Class '{node.name}' is missing a docstring.",
                "severity": "moderate",
                "location": {"file": file_path, "line": node.lineno},
                "target": node.name,
            })

        # Bad naming
        if node.name.lower() in self.bad_names:
            issues.append({
                "type": "bad_naming",
                "message": f"Class '{node.name}' uses a weak or generic name.",
                "severity": "minor",
                "location": {"file": file_path, "line": node.lineno},
                "target": node.name,
            })

        return issues
