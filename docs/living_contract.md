# DAUBA / CORE — The "Living Contract" Philosophy

## What is the Living Contract?

The Living Contract is the *explicit, upgradable set of rules and values* that DAUBA/CORE (and its users/AI) agree to follow. It acts as a "constitution" for:

* **Quality**: Clean, readable, testable code
* **Governance**: Security, compliance, and explainability
* **Self-Awareness**: Mission clarity, gap detection, and improvement

**Why organize this way?**

* **Separation of Concerns**: Each category (Quality, Governance, Self-Awareness) can be checked/upgraded by both humans and the system
* **Manifest-Driven**: YAML/JSON structure is easy for AIs and humans to reason about
* **Incremental Governance**: As DAUBA/CORE matures, new rules can be added or updated—by prompt or by code

---

## Living Contract Categories

### 1. Code Quality & Good Practices

* Readability (naming, control flow, docstrings)
* Documentation (README, in-code docs)
* Testing (unit, smoke)
* Modularity (SRP, small files)
* Error handling
* Style (PEP8/linter/formatter)

### 2. Governance & Guardrails

* Security (no secrets, no raw exec)
* Compliance (license, PII)
* Auditability (logs, traceability)
* Change Management (rollback/versioning)
* Policy as Code (YAML/JSON manifest, “constitution”)

### 3. Functional Self-Awareness

* Mission awareness (NorthStar)
* Gap detection (what’s missing?)
* Incrementalism (prefer “upgrade” over rewrite)
* Governance reflection (check own code against contract)
* Transparency (summarize changes, explain reasoning)

---

## Example: Governance Manifest (YAML)

```yaml
meta:
  name: DAUBA
  version: 0.1
  northstar: "Help users build self-improving software with AI."

governance:
  allow_writes_to: [backend/, frontend/, utils/]
  require_tests: true
  code_style: "pep8"
  docstrings: "google"
  review_required: false  # v0.1, true later
  audit_log: true

guardrails:
  restrict_imports: ["os", "sys"]  # block dangerous imports
  forbid_exec_eval: true
  max_file_size_kb: 100
  block_external_network: true

quality:
  linter: "ruff"
  formatter: "black"
  min_coverage: 40  # Minimum test coverage, to be increased

self_awareness:
  auto_gap_detection: true
  transparency_report: true
```

---

## How to Use the Living Contract

* **Always visible:** Show in docs, UI, and onboarding
* **Editable:** Users and AIs can suggest/approve contract changes
* **Enforceable:** DAUBA/CORE should check, enforce, and *explain* contract rules
* **Transparent:** Every evolution/upgrade should show how the contract is met or extended

---

## The Bottom Line

> This “Living Contract” is DAUBA/CORE’s most important asset. It is the shared language between human, system, and AI for what “good” means—and how to improve, safely, forever.
