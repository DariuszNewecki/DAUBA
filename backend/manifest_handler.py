# DAUBA/backend/manifest_handler.py
"""
Provides functionality to inject manifest metadata into prompts when the [[manifest]] directive is used.
"""

import yaml # Use the robust PyYAML library for formatting
from typing import Tuple, List
from manifest_loader import get_manifest

def inject_manifest(prompt: str) -> Tuple[str, List[str]]:
    """
    If the prompt contains [[manifest]], replace it with a formatted metadata block
    built from the manifest contents.

    Returns the enriched prompt and a list of warnings (if any).
    """
    warnings = []

    # Use a simple string check. It's efficient and clear.
    if "[[manifest]]" not in prompt:
        return prompt, warnings

    manifest = get_manifest()
    if not manifest:
        warnings.append("Manifest directive used, but manifest could not be loaded or is missing.")
        # Replace the directive with a clear note for the AI and the user
        final_prompt = prompt.replace(
            "[[manifest]]", 
            "# Manifest Context: Not Available (file not found or empty)"
        )
        return final_prompt, warnings

    # Format manifest as a clean YAML block
    try:
        # Use yaml.dump for robust and correct formatting.
        # sort_keys=False preserves the human-intended order from the YAML file.
        manifest_yaml_str = yaml.dump(
            manifest, 
            indent=2, 
            default_flow_style=False, 
            sort_keys=False
        )
        
        # Construct the final injected block using the clear START/END boundaries
        injected_text = (
            "--- START MANIFEST CONTEXT ---\n"
            f"{manifest_yaml_str}"
            "--- END MANIFEST CONTEXT ---"
        )
        
        final_prompt = prompt.replace("[[manifest]]", injected_text)
        return final_prompt, warnings

    except Exception as e:
        warnings.append(f"Error formatting manifest: {str(e)}")
        final_prompt = prompt.replace(
            "[[manifest]]", 
            f"# Manifest Context: Unavailable due to formatting error: {e}"
        )
        return final_prompt, warnings