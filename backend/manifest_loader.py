# DAUBA/backend/manifest_loader.py
"""
Handles loading and providing access to the project's manifest file.

It loads the manifest once on startup and provides a simple function
to retrieve the parsed data.
"""

import os
import yaml
import json
from typing import Dict, Any, Optional

# This variable will hold the manifest data in memory after being loaded once.
_manifest_data: Optional[Dict[str, Any]] = None
_manifest_loaded: bool = False
_manifest_path: Optional[str] = None

def load_manifest(repo_path: str) -> None:
    """
    Finds and loads the project manifest (YAML or JSON) from the repo root.
    This function should only be called once at application startup.
    """
    global _manifest_data, _manifest_loaded, _manifest_path
    if _manifest_loaded:
        return  # Already loaded or attempted to load

    # Define possible manifest filenames in order of priority
    manifest_filenames = [
        'dauba_manifest.yaml',
        'dauba_manifest.yml',
        '.dauba/project.yaml',
        'dauba_manifest.json'
    ]

    for filename in manifest_filenames:
        candidate_path = os.path.join(repo_path, filename)
        if os.path.exists(candidate_path):
            _manifest_path = candidate_path
            break

    if _manifest_path:
        try:
            with open(_manifest_path, 'r', encoding='utf-8') as f:
                if _manifest_path.endswith('.json'):
                    _manifest_data = json.load(f)
                else:
                    _manifest_data = yaml.safe_load(f)
            print(f"\u2705 Manifest loaded successfully from: {_manifest_path}")
        except Exception as e:
            print(f"\u26A0\uFE0F  Error parsing manifest file at {_manifest_path}: {e}")
            _manifest_data = None
    else:
        print("\u2139\uFE0F  No project manifest file found. Proceeding without manifest context.")

    _manifest_loaded = True

def get_manifest() -> Optional[Dict[str, Any]]:
    """
    Returns the loaded manifest data.
    Returns None if no manifest was loaded.
    """
    return _manifest_data

def is_manifest_loaded() -> bool:
    """
    Returns True if manifest has been loaded (successfully or not).
    """
    return _manifest_loaded

def get_manifest_path() -> Optional[str]:
    """
    Returns the path of the loaded manifest file, if any.
    """
    return _manifest_path
