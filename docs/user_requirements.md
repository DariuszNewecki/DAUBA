# User Requirements — DAUBA (Dumb And Ugly But Ambitious)

## Purpose

DAUBA is a minimal, web-accessible AI coding playground designed to help users write and evolve code via natural language prompts to an LLM. The system is intentionally primitive at first, but is structured for incremental, self-guided improvement and rapid onboarding of contributors.

---

## Core Users

* **Developers** (of any skill level) seeking to accelerate code writing, automate boilerplate, or experiment with LLM-powered development.
* **AI Experimenters** who want to explore or evolve codebases via conversational prompts.
* **Future contributors** interested in co-evolving the platform.

---

## User Goals

1. **Send natural language prompts to an LLM from a simple web UI.**
2. **View LLM responses immediately in the browser.**
3. **Direct the LLM to write code to files in a local project repository.**
4. **Configure LLM provider and repo path without code changes.**
5. **Evolve the system by prompting for new features or fixes over time.**
6. **(Eventually) Collaborate with other users, review changes, and maintain project safety.**

---

## Core User Stories

* *As a user, I want to type a coding or plain English prompt into a web page so that I can get help from an LLM.*

* *As a user, I want to direct the LLM to write code to a specific file in the repo, so I can bootstrap new features or automate tasks.*

* *As a user, I want to see immediately if my prompt succeeded or failed, so I know what happened.*

* *As a user, I want to configure which LLM API the system uses, so I can swap between providers or models easily.*

* *As a contributor, I want clear documentation of what works and what’s missing, so I can help evolve the tool.*

* *As a team/future user, I want to ensure unauthorized users can’t modify my codebase, so the system is safe for broader use.*

---

## Non-Goals

* DAUBA is **not** (initially) intended for:

  * Running untrusted code or evaluating code outputs directly in the browser
  * Handling multiple users, session state, or persistent chat history
  * Guaranteeing code safety, correctness, or security out-of-the-box
  * Project management or full-featured code collaboration (at MVP)

---

## Success Criteria (MVP)

* User can:

  * Load the web page and send prompts to an LLM
  * Receive and view LLM replies instantly
  * Instruct the system to write code to files in the repo (the actual file write is performed by an internal mechanism, not directly by the LLM)
  * Configure LLM provider and repo location in a single `.env` file
* All of the above with no manual code changes or CLI needed

---

## Known Limitations (Acknowledged Risks)

* No authentication or access control (initially)
* No prompt history or collaborative editing
* No syntax validation or auto-testing
* LLM can hallucinate, write unsafe or buggy code
* All changes are made as soon as the LLM replies (no review step yet)
* and many more...
