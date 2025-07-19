# DAUBA/CORE Feature & Release Map

Welcome! This document gives a quick overview of planned features, organized by release version. Use it as a living "map"—add, move, or check off items as the project grows.

```
DAUBA/CORE
└── v0.1 “The Dumb But Ambitious Workbench”
    ├── Prompt box & response area (web UI)
    ├── Send user prompts to remote LLM
    ├── Write files to local repo (via [[write:...]])
    ├── .env config loading
    └── No auth, review, or safety features

└── v0.2+ “Quality-of-Life Upgrades”
    ├── Review-before-write (“approve” button)
    ├── Simple syntax checking before write
    ├── Output preview w/ syntax highlighting
    ├── (Optional) Prompt/file history
    └── (Optional) Git integration

└── v0.3 “Safety, Security, Multi-user”
    ├── Basic authentication
    ├── File write restrictions (sandboxed to repo)
    ├── Multi-user support (sessions, prompt history)
    └── (Optional) AI prompt suggestions

└── v0.4–0.9 “Context & Smarter Coding”
    ├── Feed repo file lists/snippets as LLM context
    ├── Built-in syntax checkers, auto-formatters
    ├── Simple Test Runner
    ├── Project manifest & capability maps
    └── DAUBA suggests improvements

└── 1.0 “The Self-Upgrading Workbench”
    ├── Semi-automated code evolution (DAUBA suggests/implements features)
    ├── Self-reflection: codebase analysis, feature mapping
    ├── Editable capability/vision files via prompts
    └── Start of real self-improvement loop

└── CORE Alpha “The Last Programmer Begins”
    ├── Self-reflection & constitutional YAML governance
    ├── Dual-intent streams (business + architecture)
    └── True concept-level refactoring
```

---

**How to use:**

* When you start a new release, copy its features into GitHub Issues (1 per feature)
* Mark them off here as you complete, or update as you go
* Keep this document up-to-date for yourself and future contributors
