# DAUBA/backend/file_handler.py
"""
DAUBA Backend File Handling Module

This module manages the state of files that are ready to be written,
waiting for explicit user approval. It acts as a staging area for code changes.
"""

import os
import json
from datetime import datetime
from uuid import uuid4 # For unique identifiers for pending writes

# Configuration directory for pending writes
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "actions.log")

# In-memory storage for pending file writes.
# Structure: { 'pending_write_id': {'path': str, 'code': str, 'prompt': str, 'timestamp': str} }
pending_writes_storage = {}

def ensure_dirs():
    """Ensures that necessary directories for logs exist."""
    os.makedirs(LOG_DIR, exist_ok=True)

ensure_dirs()

def log_action(action_type: str, data: dict):
    """Log an action to the actions log file."""
    try:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action_type,
            **data
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Failed to log action: {str(e)}")

def add_pending_write(prompt: str, suggested_path: str, code: str, repo_base_path: str):
    """
    Adds a file write operation to the pending queue.
    Returns a unique ID for this pending write.
    """
    pending_id = str(uuid4())
    pending_writes_storage[pending_id] = {
        "id": pending_id,
        "prompt": prompt,
        "path": suggested_path,
        "code": code,
        "timestamp": datetime.utcnow().isoformat(),
        "repo_base_path": repo_base_path
    }
    log_action("pending_write_added", {
        "pending_id": pending_id,
        "suggested_path": suggested_path,
        "code_length": len(code),
        "code_hash": hash(code)
    })
    return pending_id

def get_pending_write(pending_id: str):
    """Retrieves a pending write by its ID."""
    return pending_writes_storage.get(pending_id)

def confirm_write(pending_id: str, repo_base_path: str):
    """
    Confirms a pending file write, writes the file, and removes it from pending.
    """
    pending_op = pending_writes_storage.get(pending_id)
    if not pending_op:
        log_action("confirm_write_failed", {"pending_id": pending_id, "error": "Pending write not found."})
        return {"write_result": "Error: Pending write not found."}

    abs_path = os.path.abspath(os.path.join(repo_base_path, pending_op['path']))
    abs_repo_path = os.path.abspath(repo_base_path)
    print(f"DEBUG: Attempting to write file to absolute path: {abs_path}")

    if not abs_path.startswith(abs_repo_path):
        log_action("confirm_write_failed", {"pending_id": pending_id, "error": "Path traversal detected."})
        del pending_writes_storage[pending_id]
        return {"write_result": "Error: Cannot write outside of repository."}

    try:
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(pending_op['code'])
        log_action("write_file_confirmed", {"pending_id": pending_id, "file_path": pending_op['path']})
        del pending_writes_storage[pending_id]
        return {"write_result": f"Wrote to {pending_op['path']}"}
    except Exception as e:
        log_action("confirm_write_failed", {"pending_id": pending_id, "error": str(e)})
        del pending_writes_storage[pending_id]
        return {"write_result": f"Failed to write file: {str(e)}"}

def reject_pending_write(pending_id: str, prompt: str):
    """
    Rejects a pending file write and logs the rejection.
    """
    pending_op = pending_writes_storage.get(pending_id)
    if not pending_op:
        log_action("reject_pending_write_failed", {"pending_id": pending_id, "error": "Pending write not found."})
        return {"status": "rejection_failed", "message": "Pending write not found."}

    log_action("pending_write_rejected", {"pending_id": pending_id, "original_prompt": prompt, "suggested_path": pending_op['path']})
    del pending_writes_storage[pending_id]
    return {"status": "write_rejected"}