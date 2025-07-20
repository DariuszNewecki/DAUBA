# DAUBA & CORE — Evolutionary Development Roadmap

## TL;DR

> **DAUBA starts dumb but upgradable. The real endgame is CORE: a system that can improve itself, reason about design, and combine code, governance, and intent in one living platform.**

---

### 🌱 DAUBA v0.1 (MVP) — “The Dumb But **Ambitious** Workbench”

* Prompt box & response area, web-based
* Send user prompts to remote LLM, get code or text reply
* LLM can write files to local repo if told (`[[write:...]]`)
* All config via `.env`
* No auth, review, history, context, or safety. Raw, honest, dangerous.
* For **explorers** and “AI optimists” who want to see software that grows itself

---

### 🚀 DAUBA v0.2+ (First Quality-of-Life Upgrades)

* Review-before-write (“approve” button for generated code)
* Simple syntax checking before code is written
* Output preview with basic syntax highlighting
* *Optional:* History of prompts & file changes
* *Optional:* Git integration for rollback

---

### 🧠 DAUBA v0.3–v0.8 — Context & Smarter Coding

> **Goal:** Evolve DAUBA from prompt-only to context-aware, quality-driven, and self-suggesting. This is the arc where DAUBA stops being dumb and starts becoming *opinionated*.

---

### 🔹 DAUBA v0.3 — Contextual Prompting

**DAUBA can finally "see" your project.**

* Feed a list of repo files or code snippets to DAUBA
* Contextual prompts now include surrounding code or folder structure
* Early support for `[[include:file.py]]` and manifest-based prompt enrichment
* Enables "suggest-in-place" prompts (e.g. add logging here)

---

### 🔹 DAUBA v0.4 — Local Quality Enforcement

**DAUBA starts to care about correctness and cleanliness.**

* Auto-formatting via tools like Black (Python) or Prettier (JS)
* Linting via Ruff (Python) or ESLint
* Syntax checkers before applying `[[write:...]]` actions
* Still no opinion about *how* to write code—just that it must *run and look clean*

> 🚨 *Note: DAUBA still does not follow best practices or patterns. Code is valid, not necessarily good. Guidance begins in v0.6.*

---

### 🔹 DAUBA v0.5 — Test-Aware Generation

**DAUBA can generate, run, and react to tests.**

* Simple test runner pane (e.g., `pytest`, `vitest`, etc.)
* DAUBA can stub or suggest unit tests for generated functions
* Post-write test execution with result capture
* Prompts can now say: "Write function AND its test"

---

### 🔹 DAUBA v0.6 — Manifest & Capability Awareness

**DAUBA now understands the purpose of your project.**

* Introduce `dauba_manifest.json` or `project.yaml`
* Manifest defines key concepts, folder roles, frameworks, and target capabilities
* DAUBA reads and references manifest for every prompt
* Allows enforcing things like: "All services must be async FastAPI modules"

> ✅ *This is the first point where DAUBA becomes standards-aware.*

---

### 🔹 DAUBA v0.7 — Suggested Improvements

**DAUBA gains judgment.**

* Highlights bad naming, missing docstrings, large functions, low cohesion
* Suggests structural fixes: split, rename, extract
* Uses project manifest as grounding for recommendations
* Interactive prompt-based refactor flow ("approve/refactor")

---

### 🔹 DAUBA v0.8 — Self-Improvement Begins

**DAUBA begins to improve its own work and its own platform.**

* Analyzes its own output and behavior over time
* Creates "upgrade tasks" for itself (e.g. refactor own test runner)
* Can propose better prompts, tighter specs, or cleaner structure
* Early loop of "DAUBA uses DAUBA"

---

### 🚨 Clarification

> Until **v0.6**, DAUBA does **not** understand or follow project architecture, coding standards, or design principles. It will only do what the prompt tells it to.
>
> Best practices enforcement begins at v0.6 (manifest-driven prompts), and becomes intelligent at v0.7+ (code smell detection and refactor suggestions).

---

---

### 🔒 DAUBA v0.9 (Safety, Security, and Multi-user)

* Basic authentication (prevent accidental/dangerous access)
* File write restrictions (can’t overwrite outside REPO\_PATH)
* Multi-user support (sessions, prompt history)
* *Optional:* AI prompt suggestions (“what can I ask?”)

---

### 🌟 DAUBA 1.0 (“The Self-Upgrading Workbench”)

* Semi-automated code evolution: DAUBA suggests new features/fixes, user approves
* Self-reflection: DAUBA can analyze its own codebase, spot missing features, suggest “upgrades”
* Documented capability maps and vision files editable via prompts
* Start of real **self-improvement loop**

---

## The CORE Roadmap: Ambitious, Unique, and New

### CORE is where DAUBA evolves into something never seen before:

| Element                                | Exists elsewhere?                       | Combined?       |
| -------------------------------------- | --------------------------------------- | --------------- |
| AI codegen for full apps               | ✅ (GPT-pilot, Aider, Cursor, etc.)      | ❌               |
| Self-rewriting systems                 | ✅ (research prototypes, meta-compilers) | ❌               |
| Constitutional YAML governance         | ✅ (OPA, CNAB, intent-based policies)    | ❌               |
| Dual-intent streams (business + arch)  | ✅ (policy-as-code, dev-guardrails)      | ❌               |
| Continuous *concept-level* refactoring | ✅ (research papers)                     | ❌               |
| **All of the above in one product**    | **❌**                                   | **This is new** |

---

### CORE: The Last Programmer Platform

**What will CORE do that nothing else can?**

* Understand **business intent** and **architecture intent** at once
* Reason about its own codebase, manifests, and governance files
* **Self-rewrite**: suggest and implement upgrades to itself
* Support **constitutional (YAML) governance** for safety and explainability
* Blend policy-as-code, business logic, and architecture in one loop
* Enable true **concept-level refactoring**—not just syntax, but goals and structure

---

### Why Start with DAUBA?

* Because **everyone** can use it, even “wannabe programmers”
* Because the *dumbest, most honest MVP* is the only foundation strong enough to grow into something ambitious (CORE)
* Because everything DAUBA lacks is a **to-do** for the next stage, and the system itself will learn to address its sins

---

## Development Phases Table

| Phase      | Name/Theme                   | Key Features                                                    | Who is it for?            |
| ---------- | ---------------------------- | --------------------------------------------------------------- | ------------------------- |
| v0.1       | “Raw”                        | Prompt, reply, file write, `.env` config                        | Solo hackers, optimists   |
| v0.2–0.3   | “Safe & Usable”              | Approve writes, syntax check, preview, history, git             | Early adopters, tinkerers |
| v0.4–0.9   | “Context & Collaboration”    | Context feeds, multi-user, auth, project manifest               | Small teams, contributors |
| 1.0        | “Self-Upgrading Workbench”   | Self-suggestions, analysis, capability map                      | Anyone curious            |
| CORE Alpha | “The Last Programmer Begins” | Self-reflection, YAML governance, dual-intent, concept-refactor | Builders, visionaries     |

---

## Final Note

> **DAUBA is not here to compete with AI copilot tools or chatbots. It is a platform to *****bootstrap***** self-improving, AI-native software—by anyone, for anyone. CORE is where the magic happens.**
