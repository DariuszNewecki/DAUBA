# DAUBA/backend/semantic_checker.py

"""
Performs static semantic checks on generated Python code.

Currently includes:
- Forbidden call detection (e.g., eval, exec)
- Import existence validation (module resolvability)
"""

import ast
import builtins
import importlib.util
import logging
import sys
from typing import List, Set

logger = logging.getLogger(__name__)

# This list can be extended with other dangerous patterns if needed
FORBIDDEN_CALLS = {
    "eval",
    "exec",
    "compile",
    "os.system",
    "subprocess.run",
    "subprocess.Popen"
}


def check_semantics(code: str) -> List[str]:
    """
    Perform static checks on the given Python code string.

    Returns a list of warnings. An empty list indicates semantic OK.
    """
    warnings = []

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"SyntaxError during semantic check: {e}"]

    imported_modules = _collect_imports(tree)
    unresolved_imports = _check_imports_exist(imported_modules)
    unsafe_calls = _find_forbidden_calls(tree)

    warnings.extend(unsafe_calls)
    warnings.extend(unresolved_imports)

    return warnings


def _collect_imports(tree: ast.AST) -> Set[str]:
    """
    Gathers top-level imported module names (not submodules).
    """
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split(".")[0])
    return imports


def _check_imports_exist(modules: Set[str]) -> List[str]:
    """
    Checks whether the imported modules can be resolved by Python.
    """
    warnings = []
    for module in modules:
        if module in sys.builtin_module_names:
            continue
        if importlib.util.find_spec(module) is None:
            warnings.append(f"Unresolvable import: '{module}' does not appear to be installed.")
    return warnings


def _find_forbidden_calls(tree: ast.AST) -> List[str]:
    """
    Detects usage of explicitly banned calls (eval, os.system, etc.).
    """
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in FORBIDDEN_CALLS:
                violations.append(f"Use of forbidden function: '{func.id}'")
            elif isinstance(func, ast.Attribute):
                full_call = _get_full_attr_name(func)
                if full_call in FORBIDDEN_CALLS:
                    violations.append(f"Use of forbidden call: '{full_call}'")
    return violations


def _get_full_attr_name(node: ast.Attribute) -> str:
    """
    Resolves a dotted attribute chain (e.g., os.path.join → 'os.path.join').
    """
    parts = []
    while isinstance(node, ast.Attribute):
        parts.insert(0, node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.insert(0, node.id)
    return ".".join(parts)
