# DAUBA/backend/main.py

import os
import re
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

from syntax_checker import check_syntax
from context_handler import inject_context, inject_includes
from manifest_handler import inject_manifest
from manifest_loader import load_manifest
from file_handler import add_pending_write, confirm_write, reject_pending_write, log_action, LOG_FILE

load_dotenv()

# --- Configuration and Constants ---
LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")
REPO_PATH = os.getenv("REPO_PATH")

if not all([LLM_API_URL, LLM_API_KEY, REPO_PATH]):
    raise RuntimeError("Missing essential environment variables: LLM_API_URL, LLM_API_KEY, REPO_PATH")

FILE_WRITE_MARKER_PATTERN = re.compile(r"\[\[write:(.+?)\]\]\s*\n?([\s\S]*)", re.MULTILINE)

app = FastAPI(title="DAUBA Backend API", version="0.6.0-alpha")

# --- Middleware and Startup Events ---
@app.on_event("startup")
async def startup_event():
    """Load the project manifest once when the application starts."""
    print("Application starting up...")
    load_manifest(REPO_PATH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class PromptRequest(BaseModel):
    prompt: str

class WriteFileRequest(BaseModel):
    pending_id: str

class RejectWriteRequest(BaseModel):
    pending_id: str
    prompt: str

# --- API Endpoints ---
@app.post("/ask")
def ask_llm(data: PromptRequest):
    original_prompt = data.prompt
    all_warnings = []

    # --- Prompt Enrichment Chain ---
    # Step 1: Process [[manifest]] directive
    prompt_after_manifest, manifest_warnings = inject_manifest(original_prompt)
    all_warnings.extend(manifest_warnings)
    
    # Step 2: Process [[include:...]] directives
    prompt_after_includes, include_warnings = inject_includes(prompt_after_manifest, REPO_PATH)
    all_warnings.extend(include_warnings)

    # Step 3: Process [[context:...]] directives
    enriched_prompt, context_warnings = inject_context(prompt_after_includes, REPO_PATH)
    all_warnings.extend(context_warnings)
    # --- End of Chain ---

    headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": enriched_prompt}],
        "temperature": 0.7,
        "max_tokens": 8192
    }

    try:
        resp = requests.post(LLM_API_URL, headers=headers, json=body)
        resp.raise_for_status()
        llm_content = resp.json()["choices"][0]["message"]["content"]

        # Prepend any warnings from the enrichment process to the final output
        if all_warnings:
            warning_text = "Note: The following issues occurred while loading content:\n- " + "\n- ".join(all_warnings)
            llm_content = f"{warning_text}\n\n---\n\n{llm_content}"

        match = FILE_WRITE_MARKER_PATTERN.search(llm_content)

        if match:
            suggested_path = match.group(1).strip()
            code_to_write = match.group(2).strip()
            
            # Heuristic to clean up fenced code blocks
            code_block_match = re.search(r"```(?:\w+)?\n([\s\S]*?)\n```", code_to_write)
            if code_block_match:
                code_to_write = code_block_match.group(1).strip()

            is_valid, message = check_syntax(suggested_path, code_to_write)
            if not is_valid:
                log_action("syntax_check_failed", {"prompt": original_prompt, "warnings": all_warnings, "error": message})
                return {"output": f"Syntax error rejected:\n\n{message}"}

            pending_id = add_pending_write(
                prompt=original_prompt,
                suggested_path=suggested_path,
                code=code_to_write,
                repo_base_path=REPO_PATH
            )
            return {"pending_write_id": pending_id, "file_path": suggested_path, "code": code_to_write}
        else:
            log_action("ask", {
                "prompt": original_prompt,
                "final_prompt_length": len(enriched_prompt),
                "warnings": all_warnings,
                "response": llm_content
            })
            return {"output": llm_content}

    except Exception as e:
        log_action("ask_error", {"prompt": original_prompt, "error": str(e)})
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.post("/confirm_write")
def confirm_write_operation(data: WriteFileRequest):
    result = confirm_write(data.pending_id, REPO_PATH)
    if "error" in result.get("write_result", ""):
        raise HTTPException(status_code=500, detail=result["write_result"])
    return result

@app.post("/reject_write")
def reject_write_operation(data: RejectWriteRequest):
    result = reject_pending_write(data.pending_id, data.prompt)
    if "rejection_failed" in result.get("status", ""):
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@app.get("/history")
def get_history():
    try:
        history_entries = []
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        history_entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        print(f"Warning: Skipping malformed line in actions.log: {line.strip()}")
        history_entries.reverse()
        return history_entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read history log: {e}")

@app.get("/")
def root():
    return {"DAUBA": "alive"}