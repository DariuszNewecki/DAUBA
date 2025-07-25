# DAUBA/backend/file_handler.py

"""
DAUBA Backend File Handling Module

Handles staging, writing, and optionally Git-committing file changes.
Adds thread-safety to support concurrent operations reliably.
"""

import os
import json
import subprocess
import threading
from datetime import datetime
from uuid import uuid4

from test_runner import run_tests  # ✅ NEW IMPORT

# --- Constants ---
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "actions.log")

# --- Global State ---
pending_writes_storage = {}
_storage_lock = threading.Lock()

os.makedirs(LOG_DIR, exist_ok=True)

# --- Logging ---
def log_action(action_type: str, data: dict):
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


# --- Pending Write Operations ---
def add_pending_write(prompt: str, suggested_path: str, code: str, repo_base_path: str) -> str:
    pending_id = str(uuid4())
    with _storage_lock:
        pending_writes_storage[pending_id] = {
            "id": pending_id,
            "prompt": prompt,
            "path": suggested_path,
            "code": code,
            "timestamp": datetime.utcnow().isoformat(),
            "repo_base_path": repo_base_path,
        }
    log_action("pending_write_added", {
        "pending_id": pending_id,
        "suggested_path": suggested_path,
        "code_length": len(code),
        "code_hash": hash(code)
    })
    return pending_id


def get_pending_write(pending_id: str):
    with _storage_lock:
        return pending_writes_storage.get(pending_id)


def reject_pending_write(pending_id: str, prompt: str):
    with _storage_lock:
        pending_op = pending_writes_storage.get(pending_id)
        if not pending_op:
            return {"status": "rejection_failed", "message": "Pending write not found."}
        del pending_writes_storage[pending_id]
    log_action("pending_write_rejected", {
        "pending_id": pending_id,
        "original_prompt": prompt,
        "suggested_path": pending_op['path']
    })
    return {"status": "write_rejected"}


# --- Git Helpers ---
def _run_git_command(command: list[str], repo_path: str):
    try:
        result = subprocess.run(
            command,
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )
        return result
    except FileNotFoundError:
        raise RuntimeError("Git command not found.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git command failed: {e.stderr.strip()}")


# --- Confirm Write ---
def confirm_write(pending_id: str, repo_base_path: str):
    with _storage_lock:
        pending_op = pending_writes_storage.get(pending_id)
        if not pending_op:
            return {"write_result": "Error: Pending write not found."}

    abs_repo_path = os.path.abspath(repo_base_path)
    abs_file_path = os.path.abspath(os.path.join(abs_repo_path, pending_op['path']))

    if os.path.commonpath([abs_repo_path, abs_file_path]) != abs_repo_path:
        with _storage_lock:
            del pending_writes_storage[pending_id]
        return {"write_result": "Error: Cannot write outside of repository."}

    try:
        os.makedirs(os.path.dirname(abs_file_path), exist_ok=True)
        with open(abs_file_path, "w", encoding="utf-8") as f:
            f.write(pending_op['code'])

        log_action("write_file_confirmed", {
            "pending_id": pending_id,
            "file_path": pending_op['path']
        })

        git_message = ""
        if os.path.isdir(os.path.join(abs_repo_path, '.git')):
            try:
                _run_git_command(['git', 'add', pending_op['path']], abs_repo_path)
                commit_msg = f"feat(dauba): Modify {pending_op['path']} via prompt"
                _run_git_command(['git', 'commit', '-m', commit_msg], abs_repo_path)
                result = _run_git_command(['git', 'rev-parse', 'HEAD'], abs_repo_path)
                commit_hash = result.stdout.strip()
                git_message = f"and created commit {commit_hash[:7]}"
            except RuntimeError as e:
                log_action("git_commit_failed", {
                    "pending_id": pending_id,
                    "error": str(e)
                })
                git_message = f"\nWARNING: Git commit failed: {e}"

        # ✅ NEW: Run tests and log results
        test_results = run_tests(silent=True)
        log_action("test_results_after_write", {
            "pending_id": pending_id,
            "test_summary": test_results.get("summary"),
            "tests_passed": test_results.get("exit_code") == "0"
        })

        return_message = f"Wrote to {pending_op['path']} {git_message}"

    except Exception as e:
        log_action("confirm_write_failed", {
            "pending_id": pending_id,
            "error": str(e)
        })
        return_message = f"Failed to write file: {str(e)}"

    with _storage_lock:
        pending_writes_storage.pop(pending_id, None)

    return {"write_result": return_message, "test_summary": test_results.get("summary", "N/A")}