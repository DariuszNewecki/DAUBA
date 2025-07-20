# DAUBA/backend/file_handler.py
"""
DAUBA Backend File Handling Module

Manages staging, writing, and now, auto-committing of approved file changes.
"""

import os
import json
import subprocess # NEW: Import the subprocess module
from datetime import datetime
from uuid import uuid4

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "actions.log")

pending_writes_storage = {}

def ensure_dirs():
    os.makedirs(LOG_DIR, exist_ok=True)

ensure_dirs()

def log_action(action_type: str, data: dict):
    try:
        log_entry = { "timestamp": datetime.utcnow().isoformat(), "action": action_type, **data }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Failed to log action: {str(e)}")

def add_pending_write(prompt: str, suggested_path: str, code: str, repo_base_path: str):
    pending_id = str(uuid4())
    pending_writes_storage[pending_id] = {
        "id": pending_id, "prompt": prompt, "path": suggested_path, "code": code,
        "timestamp": datetime.utcnow().isoformat(), "repo_base_path": repo_base_path
    }
    log_action("pending_write_added", {
        "pending_id": pending_id, "suggested_path": suggested_path,
        "code_length": len(code), "code_hash": hash(code)
    })
    return pending_id

def get_pending_write(pending_id: str):
    return pending_writes_storage.get(pending_id)

def reject_pending_write(pending_id: str, prompt: str):
    pending_op = pending_writes_storage.get(pending_id)
    if not pending_op:
        return {"status": "rejection_failed", "message": "Pending write not found."}
    log_action("pending_write_rejected", {
        "pending_id": pending_id, "original_prompt": prompt, "suggested_path": pending_op['path']
    })
    del pending_writes_storage[pending_id]
    return {"status": "write_rejected"}


# --- MODIFIED confirm_write FUNCTION ---

def _run_git_command(command: list[str], repo_path: str):
    """Helper function to run a Git command and handle errors."""
    try:
        # check=True will raise CalledProcessError if the command fails
        result = subprocess.run(
            command,
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )
        return result
    except FileNotFoundError:
        # This happens if 'git' is not installed or not in the system's PATH
        raise RuntimeError("Git command not found. Is Git installed and in your PATH?")
    except subprocess.CalledProcessError as e:
        # Re-raise with a more informative error message including stderr
        raise RuntimeError(f"Git command failed: {e.stderr}")


def confirm_write(pending_id: str, repo_base_path: str):
    """
    Confirms a pending file write, writes the file, and if in a Git repo,
    automatically adds and commits the change.
    """
    pending_op = pending_writes_storage.get(pending_id)
    if not pending_op:
        return {"write_result": "Error: Pending write not found."}

    abs_path = os.path.abspath(os.path.join(repo_base_path, pending_op['path']))
    abs_repo_path = os.path.abspath(repo_base_path)

    if not abs_path.startswith(abs_repo_path):
        del pending_writes_storage[pending_id]
        return {"write_result": "Error: Cannot write outside of repository."}

    try:
        # Step 1: Write the file to disk
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(pending_op['code'])
        
        log_action("write_file_confirmed", {"pending_id": pending_id, "file_path": pending_op['path']})
        
        # Step 2: Check if it's a Git repo
        git_dir = os.path.join(repo_base_path, '.git')
        if not os.path.isdir(git_dir):
            del pending_writes_storage[pending_id]
            return {"write_result": f"Wrote to {pending_op['path']} (not a Git repo)."}

        # Step 3: Run Git commands
        try:
            # Git Add
            _run_git_command(['git', 'add', pending_op['path']], repo_base_path)
            
            # Git Commit
            commit_message = f"feat(dauba): Modify {pending_op['path']} via prompt"
            _run_git_command(['git', 'commit', '-m', commit_message], repo_base_path)
            
            # Get the latest commit hash to return to the user
            result = _run_git_command(['git', 'rev-parse', 'HEAD'], repo_base_path)
            commit_hash = result.stdout.strip()
            
            git_message = f"and created commit {commit_hash[:7]}"

        except RuntimeError as e:
            # This catches failures from the helper function
            log_action("git_commit_failed", {"pending_id": pending_id, "error": str(e)})
            git_message = f"\nWARNING: Git commit failed: {str(e)}"

        del pending_writes_storage[pending_id]
        return {"write_result": f"Wrote to {pending_op['path']} {git_message}"}

    except Exception as e:
        log_action("confirm_write_failed", {"pending_id": pending_id, "error": str(e)})
        del pending_writes_storage[pending_id]
        return {"write_result": f"Failed to write file: {str(e)}"}