# DAUBA/backend/syntax_checker.py
"""
A simple syntax checker utility for DAUBA.

This module provides functions to validate the syntax of generated code
before it is staged for review or written to a file.
"""

import ast

def check_syntax(file_path: str, code: str) -> tuple[bool, str]:
    """
    Checks the syntax of a given code string based on its file extension.

    Currently supports Python (.py) files. For other file types, it assumes
    the syntax is valid.

    Args:
        file_path (str): The path of the file to be written (used to determine language).
        code (str): The source code to check.

    Returns:
        tuple[bool, str]: A tuple containing:
                          - A boolean indicating if the syntax is valid.
                          - A message (either 'Syntax is valid' or an error string).
    """
    if file_path.endswith(".py"):
        try:
            ast.parse(code)
            return (True, "Python syntax is valid.")
        except SyntaxError as e:
            # Provide a helpful error message from the exception
            error_message = f"Invalid Python syntax: {e.text.strip()}\nOn line {e.lineno}, column {e.offset}: {e.msg}"
            return (False, error_message)
    
    # For now, we don't check other file types, so we approve them by default.
    return (True, "Syntax check skipped for non-Python file.")