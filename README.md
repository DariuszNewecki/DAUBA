![License: MIT](https://img.shields.io/github/license/DariuszNewecki/DAUBA)
# DAUBA — Dumb And Ugly But Ambitious: The Self-Improving LLM Coding Workbench

## What is this?

A brutally minimal web tool that lets you:

* Send prompts to a remote LLM (configurable via `.env`)
* Write code directly to a local repo via LLM output
* See responses in a chat-like interface

No user management. No code review. No guardrails. Just raw power and a “let’s evolve this together” mentality.

---

## Why “Dumb And Ugly But Ambitious”?

This project **starts as the dumbest possible thing that can work**—by design.

* **MVP is intentionally primitive** (and a bit dangerous!) so it can grow itself through your prompts and contributions.
* Every known “bad habit” or risk is accepted as a deliberate tradeoff, because the most important feature is the *ability to self-improve, incrementally, forever*.

---

## Minimum Features (MVP)

* Web UI with one input box and a send button
* Output area for LLM responses
* `.env`-driven LLM API configuration
* Backend can write (or overwrite) local files based on prompt/LLM output
* Everything else (auth, review, previews, etc) is future work—maybe by the tool itself!

---

## ✅ What Works Today (v0.4 Highlights)

DAUBA is no longer just a raw MVP. The following features are **fully working** in the latest release (`v0.4.0`):

- `[[write:file.py]]`: Writes code to disk, but only after passing:
  - ✅ Black formatting
  - ✅ Ruff linting
  - ✅ Syntax checking
  - ✅ Semantic validation (e.g. no `eval()`, no bad imports)
- `[[include:file.py]]`: Inject full file or specific function/class
- `[[context:...]]`: Inject multiple files with automatic AST clipping
- `[[suggest:file.py:10–20]]`: Add line-range context to your prompts
- `[[manifest]]`: Injects your project manifest into prompts
- Safe by default: DAUBA refuses to write or read outside your repo root
- Git integration: Auto-commits approved writes with prompt-based commit messages

> **v0.4 = DAUBA gets its first sense of correctness.**

To see what’s coming next, check the [Roadmap](docs/roadmap.md).

---

## Known Limitations and Sins (that we intend to fix)

* **Security:** No authentication. If you run this on an open network, you’re asking for trouble.
* **Dangerous Writes:** LLM can overwrite any local file you point it at. Double-check prompts!
* **LLM Hallucination:** The AI might generate code that breaks things. *You* are the reviewer…for now.
* **No Undo:** Accidentally nuked a file? Use git or your file system backup.
* **No Multi-user or History:** One chat window, one user. That’s it.
* **API Keys in .env:** Don’t commit your .env file!

**All of these are “known sins”—we accept them, but expect the system (and its users) to fix them over time.**

---

## How to Run (Local Quickstart)

1. **Clone this repo**

   ```bash
   git clone <repo-url>
   cd <repo-folder>
   ```

2. **Fill in your `.env` file** (see sample below)

3. **Start the backend**

   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start the frontend**

   ```bash
   cd frontend
   npm install
   npm run dev -- --host 0.0.0.0
   ```

5. **Open your browser:**
   [http://<server-ip>:5173](http://<server-ip>:5173)
   (or whatever port your frontend uses)

![DAUBA Workbench Screenshot](docs/UI.png)

---

## Example Prompts (How To Evolve the Tool)

* "Create a function in utils/math.py that adds two numbers"
* "Write a test for the function in tests/test_math.py"
* "Add a page to the UI that lists all Python files in the repo"
* "Implement syntax checking for all generated code before writing"

*(Remember: The tool can get smarter as you tell it what to do!)*

---

## How To Contribute

* Try the tool! Break it, fix it, or prompt it to fix itself.
* Add features by prompt, or by pull request if you prefer.
* Every improvement—no matter how small—is progress.
* **Warning:** This project is expected to look ugly and unsafe at first. That’s the plan. Help it get better, bit by bit.
* If you want to explain *why* you fixed something, add to `docs/vision.md`!

---

## .env Sample

```env
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_API_KEY=sk-xxxxxxx
REPO_PATH=/absolute/path/to/your/local/repo
```

---

## The Vision

This is not just a coding tool—it’s a living workbench for **incremental, AI-powered self-improvement**.

We believe in starting ugly, moving fast, and fixing our sins as we go—by code, by prompt, or by community.

**Join us. Help the system evolve, one prompt at a time.**

---

## Versioning & Releases

Every milestone is preserved and tagged:

- `v0.1`: Raw prompt → response → write flow (no checks)
- `v0.2`: Approve-before-write, syntax check
- `v0.3`: Context awareness (`[[include]]`, `[[suggest]]`, `[[context]]`)
- `v0.4`: Local quality enforcement — format, lint, check, and commit
- `main`: Bleeding edge. Tracks ongoing development toward v0.5+

See the [Releases tab](https://github.com/DariuszNewecki/DAUBA/releases) for full changelogs.
