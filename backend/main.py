# DuBU/backend/main.py
"""
DuBU Backend API Module

This module provides the FastAPI backend for the DuBU (Developer's Ultimate Buddy) application.
It handles communication with LLM APIs and file operations for code generation.
"""

import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
LLM_API_URL = os.getenv("LLM_API_URL")  # URL for the LLM API endpoint
LLM_API_KEY = os.getenv("LLM_API_KEY")  # API key for authentication
REPO_PATH = os.getenv("REPO_PATH")      # Base path for the code repository

app = FastAPI(title="DuBU Backend API",
              description="API backend for DuBU code generation tool",
              version="0.1.0")

# Configure CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Note: For MVP only - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    """Request model for LLM prompt endpoint.
    
    Attributes:
        prompt (str): The input prompt to send to the LLM.
    """
    prompt: str

class WriteFileRequest(BaseModel):
    """Request model for direct file writing endpoint.
    
    Attributes:
        path (str): Relative path to the file from REPO_PATH
        code (str): Code content to write to the file
    """
    path: str
    code: str

@app.post("/ask")
def ask_llm(data: PromptRequest):
    """Endpoint to send prompts to LLM and optionally write generated code.
    
    Processes the prompt through the LLM API and handles special 'write file' markers
    in the response to automatically write generated code to files.
    
    Args:
        data (PromptRequest): Contains the prompt string to send to LLM
        
    Returns:
        dict: Contains either:
            - output: LLM response content
            - write_result: File operation result (if file writing was triggered)
            - error: If LLM API call failed
    """
    # Prepare headers and body for LLM API request
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "deepseek-chat",  # Default model - can be parameterized later
        "messages": [{"role": "user", "content": data.prompt}],
        "temperature": 0.7,        # Controls randomness of output
        "max_tokens": 2048        # Limit response length
    }
    
    # Make request to LLM API
    resp = requests.post(LLM_API_URL, headers=headers, json=body)
    if resp.status_code != 200:
        return {"error": f"LLM API error: {resp.text}"}
    
    # Extract content from successful response
    content = resp.json()["choices"][0]["message"]["content"]
    
    # Check for file write marker in the prompt (naive MVP implementation)
    if "[[write:" in data.prompt:
        try:
            # Parse the file path and code from LLM response
            marker_start = content.index("[[write:") + 8
            marker_end = content.index("]]", marker_start)
            file_path = content[marker_start:marker_end].strip()
            
            # Extract code (everything after the marker)
            code_start = marker_end + 2
            code = content[code_start:].lstrip("\n")
            
            # Create directories if needed and write file
            abs_path = os.path.join(REPO_PATH, file_path)
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(code)
                
            write_result = f"Wrote to {file_path}"
        except Exception as e:
            write_result = f"Failed to write file: {str(e)}"
            
        return {"output": content, "write_result": write_result}
    else:
        return {"output": content}

@app.post("/write_file")
def write_file(data: WriteFileRequest):
    """Endpoint to directly write code to a file.
    
    Args:
        data (WriteFileRequest): Contains path and code to write
        
    Returns:
        dict: Contains write_result with operation status
    """
    try:
        # Ensure directory exists and write file
        abs_path = os.path.join(REPO_PATH, data.path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(data.code)
        return {"write_result": f"Wrote to {data.path}"}
    except Exception as e:
        return {"write_result": f"Failed to write file: {str(e)}"}

@app.get("/")
def root():
    """Health check endpoint.
    
    Returns:
        dict: Simple status message
    """
    return {"DuBU": "alive"}
