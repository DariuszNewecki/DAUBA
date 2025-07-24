# backend/suggestion_engine.py

"""
Generates fix suggestions based on code quality issues.

Transforms analyzer results into structured, actionable recommendations.
"""

from typing import List, Dict


def suggest_fixes(issues: List[Dict]) -> List[Dict]:
    """
    Takes a list of code quality issues and returns structured suggestions.

    Args:
        issues (List[Dict]): Issues reported by CodeQualityAnalyzer.

    Returns:
        List[Dict]: Suggestions with added "suggestion" and "refactor_plan".
    """
    suggestions = []

    for issue in issues:
        suggestion = issue.copy()
        issue_type = issue.get("type")
        target = issue.get("target", "unknown")

        if issue_type == "missing_docstring":
            suggestion["suggestion"] = f"Add a docstring that explains what '{target}' does."
            suggestion["refactor_plan"] = [f"Insert a triple-quoted docstring below the definition of '{target}'."]
        
        elif issue_type == "bad_naming":
            better_name = suggest_better_name(target)
            suggestion["suggestion"] = f"Rename '{target}' to something more descriptive like '{better_name}'."
            suggestion["refactor_plan"] = [f"Replace all usages of '{target}' with '{better_name}'."]
        
        elif issue_type == "too_long":
            suggestion["suggestion"] = f"Split the function '{target}' into smaller helper functions."
            suggestion["refactor_plan"] = [
                f"Identify logical sections inside '{target}' and extract them into named helper functions.",
                f"Call those helper functions from within '{target}'."
            ]
        
        elif issue_type == "low_cohesion":
            suggestion["suggestion"] = f"Consider breaking '{target}' into multiple functions to improve cohesion."
            suggestion["refactor_plan"] = [
                f"Group related statements in '{target}' and move them into new functions.",
                f"Make the main function shorter and more readable."
            ]

        elif issue_type == "syntax_error":
            suggestion["suggestion"] = "Fix the syntax error before proceeding."
            suggestion["refactor_plan"] = ["Check line and column for issue and repair it manually."]
        
        else:
            # Fallback for unhandled issue types
            suggestion["suggestion"] = f"Review '{target}' for possible improvements."
            suggestion["refactor_plan"] = ["Manually inspect and refactor if needed."]

        suggestions.append(suggestion)

    return suggestions


def suggest_better_name(original_name: str) -> str:
    """
    Generates a better placeholder name based on common patterns.

    Args:
        original_name (str): The original weak name.

    Returns:
        str: A more descriptive placeholder name.
    """
    placeholders = {
        "foo": "process_data",
        "bar": "handle_request",
        "data": "raw_input",
        "x": "value_x",
        "y": "value_y",
        "z": "result_z",
        "temp": "temporary_result",
        "test": "run_test",
    }
    return placeholders.get(original_name.lower(), f"{original_name}_refactored")
