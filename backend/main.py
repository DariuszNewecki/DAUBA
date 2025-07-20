# DAUBA/backend/main.py
"""
DAUBA Backend API Module
Implements the user's desired review/approval flow with syntax checking.
"""

import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

# Import our new syntax checker
from syntax_checker import check_syntax 
from file_handler import add_pending_write, confirm_write, reject_pending_write, log_action

load_dotenv()

LLM_API_URL = os.getenv("LLM_API_URL")
LLM_API_KEY = os.getenv("LLM_API_KEY")
REPO_PATH = os.getenv("REPO_PATH")

if not all([LLM_API_URL, LLM_API_KEY, REPO_PATH]):
    raise RuntimeError("Missing essential environment variables: LLM_API_URL, LLM_API_KEY, REPO_PATH")

FILE_WRITE_MARKER_PATTERN = re.compile(r"\[\[write:(.+?)\]\]\s*\n?([\s\S]*)", re.MULTILINE)

# Version updated to reflect this new feature work
app = FastAPI(title="DAUBA Backend API", version="0.4.1-alpha") 

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
    headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}
    body = {"model": "deepseek-chat", "messages": [{"role": "user", "content": data.prompt}], "temperature": 0.7, "max_tokens": 4096}

    try:
        resp = requests.post(LLM_API_URL, headers=headers, json=body)
        resp.raise_for_status()
        llm_content = resp.json()["choices"][0]["message"]["content"]
        match = FILE_WRITE_MARKER_PATTERN.search(llm_content)

        if match:
            suggested_path = match.group(1).strip()
            code_to_write = match.group(2).strip()
            
            # Heuristic to clean up code block if fenced
            code_block_match = re.search(r"```(?:\w+)?\n([\s\S]*?)\n```", code_to_write)
            if code_block_match:
                code_to_write = code_block_match.group(1).strip()

            # --- NEW SYNTAX CHECK STEP ---
            is_valid, message = check_syntax(suggested_path, code_to_write)

            if not is_valid:
                # If syntax is bad, log it and return an error message to the user.
                log_action("syntax_check_failed", {
                    "prompt": data.prompt,
                    "file_path": suggested_path,
                    "error": message
                })
                # We return a regular 'output' so the frontend displays it as a message.
                return {"output": f"AI-generated code has a syntax error and was rejected:\n\n{message}\n\nPlease try rephrasing your prompt."}
            # --- END OF NEW STEP ---

            # If syntax is valid, proceed as before.
            pending_id = add_pending_write(
                prompt=data.prompt,
                suggested_path=suggested_path,
                code=code_to_write,
                repo_base_path=REPO_PATH
            )
            return {"pending_write_id": pending_id, "file_path": suggested_path, "code": code_to_write}
        else:
            log_action("ask", {"prompt": data.prompt, "response": llm_content})
            return {"output": llm_content}
    except Exception as e:
        log_action("ask_error", {"prompt": data.prompt, "error": str(e)})
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# ... (the rest of the /confirm_write, /reject_write, and / endpoints are unchanged) ...

@app.post("/confirm_write")
def confirm_write_operation(data: WriteFileRequest):
    result = confirm_write(data.pending_id, REPO_PATH)
    if "error" in result.get("write_result", ""):
        raise HTTPException(status_code=500, detail=result["write_result"])
    return result

@app.post("/reject_write")
def reject_write_operation(data: RejectWriteRequest):
    result = reject_pending_write(data.pending_id, data.prompt)
    if result.get("status") == "rejection_failed":
        raise HTTPException(status_code=400, detail=result.get("message"))
    return result

@app.get("/")
def root():
    return {"DAUBA": "alive"}