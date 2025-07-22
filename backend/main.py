# DAUBA/backend/main.py

import os
import re
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

from black_formatter import format_code_with_black  # NEW: code formatter
from syntax_checker import check_syntax
# from context_handler import inject_context, inject_includes
from context_handler import inject_context
from include_handler import inject_includes

from manifest_handler import inject_manifest
from suggest_handler import inject_suggestions
from manifest_loader import load_manifest
from file_handler import add_pending_write, confirm_write, reject_pending_write, log_action, LOG_FILE

load_dotenv()

LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")
REPO_PATH = os.getenv("REPO_PATH")

if not all([LLM_API_URL, LLM_API_KEY, REPO_PATH]):
    raise RuntimeError("Missing essential environment variables: LLM_API_URL, LLM_API_KEY, REPO_PATH")

FILE_WRITE_MARKER_PATTERN = re.compile(r"\[\[write:(.+?)\]\]\s*\n?([\s\S]*)", re.MULTILINE)

app = FastAPI(title="DAUBA Backend API", version="0.4.1-alpha")

@app.on_event("startup")
async def startup_event():
    print("Application starting up...")
    load_manifest(REPO_PATH)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str

class WriteFileRequest(BaseModel):
    pending_id: str

class RejectWriteRequest(BaseModel):
    pending_id: str
    prompt: str

@app.post("/ask")
def ask_llm(data: PromptRequest):
    original_prompt = data.prompt
    all_warnings = []

    # Enrichment pipeline
    prompt1, manifest_warnings = inject_manifest(original_prompt)
    all_warnings.extend(manifest_warnings)

    prompt2, suggest_warnings = inject_suggestions(prompt1, REPO_PATH)
    all_warnings.extend(suggest_warnings)

    prompt3, include_warnings = inject_includes(prompt2, REPO_PATH)
    all_warnings.extend(include_warnings)

    enriched_prompt, context_warnings = inject_context(prompt3, REPO_PATH)
    all_warnings.extend(context_warnings)

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

        if all_warnings:
            warning_text = "Note: The following issues occurred while loading content:\n- " + "\n- ".join(all_warnings)
            llm_content = f"{warning_text}\n\n---\n\n{llm_content}"

        match = FILE_WRITE_MARKER_PATTERN.search(llm_content)

        if match:
            suggested_path = match.group(1).strip()
            code_to_write = match.group(2).strip()

            code_block_match = re.search(r"```(?:\w+)?\n([\s\S]*?)\n```", code_to_write)
            if code_block_match:
                code_to_write = code_block_match.group(1).strip()

            formatted_code, format_error = format_code_with_black(code_to_write)
            if format_error:
                log_action("formatting_failed", {"prompt": original_prompt, "error": format_error})
                return {"output": f"Black formatting failed:\n\n{format_error}"}
            code_to_write = formatted_code  # Use formatted version

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
            return {"pending_widget_id": pending_id, "file_path": suggested_path, "code": code_to_write}

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
        if not os.path.exists(LOG_FILE):
            return []
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            history_entries = [json.loads(line) for line in f if line.strip()]
        history_entries.reverse()
        return history_entries
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not read history log: {e}")

@app.get("/")
def root():
    return {"DAUBA": "alive"}
