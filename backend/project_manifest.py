# DAUBA/backend/project_manifest.py

"""
Manifest Loader for DAUBA

Reads and parses a project manifest file (JSON or YAML) that defines
project intent, structure, capabilities, and enforcement rules.
"""

import os
import json
import yaml
from typing import Any, Dict, Optional

_manifest_data: Optional[Dict[str, Any]] = None
_manifest_path: Optional[str] = None

DEFAULT_MANIFEST_FILES = [
    "dauba_manifest.json",
    "project_manifest.json",
    "project.yaml",
    "project.yml"
]


def load_manifest(project_root: str) -> None:
    """
    Loads the manifest file from disk into memory.

    Args:
        project_root (str): Absolute path to the project root folder.
    Raises:
        FileNotFoundError: If no manifest file is found.
        ValueError: If the manifest file cannot be parsed.
    """
    global _manifest_data, _manifest_path

    for filename in DEFAULT_MANIFEST_FILES:
        candidate = os.path.join(project_root, filename)
        if os.path.exists(candidate):
            _manifest_path = candidate
            with open(candidate, "r", encoding="utf-8") as f:
                if filename.endswith(".json"):
                    _manifest_data = json.load(f)
                elif filename.endswith((".yaml", ".yml")):
                    _manifest_data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported manifest format: {filename}")
            return

    raise FileNotFoundError(f"No manifest file found in {project_root}")


def get_manifest() -> Dict[str, Any]:
    """
    Returns the current parsed manifest data.

    Raises:
        RuntimeError: If no manifest is loaded.
    """
    if _manifest_data is None:
        raise RuntimeError("Manifest not loaded. Call load_manifest() first.")
    return _manifest_data


def get_required_capabilities() -> list[str]:
    """
    Returns a list of required capabilities from the manifest, if declared.
    """
    manifest = get_manifest()
    return manifest.get("required_capabilities", [])


def get_project_goals() -> str:
    """
    Returns a high-level project mission or intent, if defined.
    """
    manifest = get_manifest()
    return manifest.get("intent", "No intent specified.")


def get_raw_manifest_path() -> Optional[str]:
    """
    Returns the path to the loaded manifest file.
    """
    return _manifest_path
