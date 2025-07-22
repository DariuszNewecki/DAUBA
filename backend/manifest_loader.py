# DAUBA/backend/manifest_loader.py

"""
Loads and provides access to the project's manifest file.

Supports YAML or JSON formats, loaded once at startup.
"""

import os
import yaml
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# In-memory cache
_manifest_data: Optional[Dict[str, Any]] = None
_manifest_loaded: bool = False
_manifest_path: Optional[str] = None


def load_manifest(repo_path: str) -> None:
    """
    Attempts to locate and load a manifest file from the given repo path.

    Supported filenames (first match wins):
      - dauba_manifest.yaml
      - dauba_manifest.yml
      - .dauba/project.yaml
      - dauba_manifest.json
    """
    global _manifest_data, _manifest_loaded, _manifest_path

    if _manifest_loaded:
        return  # Already loaded or attempted to load

    manifest_filenames = [
        "dauba_manifest.yaml",
        "dauba_manifest.yml",
        ".dauba/project.yaml",
        "dauba_manifest.json",
    ]

    for filename in manifest_filenames:
        candidate_path = os.path.join(repo_path, filename)
        if os.path.exists(candidate_path):
            _manifest_path = candidate_path
            break

    if _manifest_path:
        try:
            with open(_manifest_path, "r", encoding="utf-8") as f:
                if _manifest_path.endswith(".json"):
                    _manifest_data = json.load(f)
                else:
                    _manifest_data = yaml.safe_load(f)

            logger.info(f"✅ Manifest loaded from: {_manifest_path}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to parse manifest at {_manifest_path}: {e}")
            _manifest_data = None
    else:
        logger.info("ℹ️  No project manifest found. Continuing without manifest context.")

    _manifest_loaded = True


def get_manifest() -> Optional[Dict[str, Any]]:
    """Returns the parsed manifest data, or None if unavailable."""
    return _manifest_data


def is_manifest_loaded() -> bool:
    """Returns True if load_manifest() has been run."""
    return _manifest_loaded


def get_manifest_path() -> Optional[str]:
    """Returns the resolved manifest file path, or None."""
    return _manifest_path
