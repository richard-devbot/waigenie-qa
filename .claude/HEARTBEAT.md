# HEARTBEAT.md — WAIGenie Project Health & Phase Tracker

Live status of the waigenie project. Update this file when issues are closed or phases shift.
Last updated: 2026-03-16

---

## Current Status

| Dimension | Status |
|-----------|--------|
| Main branch | ✅ Stable |
| Last merged PR | PR #50 — security hardening + model correctness |
| Open issues | ~40 |
| Active phase | Phase 2: Browser Intelligence |
| CI | No automated CI yet (Phase 4 scope) |

---

## Phase Progress

### ✅ Phase 1 — Intelligence Core (DONE)
> Issues #22–25 · Branch: `phase-1-intelligence-core` · Merged: PR #42

| Issue | Title | Status |
|-------|-------|--------|
| #22 | Pydantic structured outputs for all 5 agents | ✅ |
| #23 | ReasoningTools (chain-of-thought) for all agents | ✅ |
| #24 | Agno Workflow 2.0 — parallel TestCraft + GherkinGen | ✅ |
| #25 | Agno Team coordinate mode — QA Master Orchestrator | ✅ |

**Security hardening (PR #50 — merged 2026-03-16):**
- `secrets.compare_digest()` for timing-safe auth
- `SECRET_KEY` startup validation when `API_KEY_REQUIRED=True`
- `GherkinScenario.given/when/then` enforced as `List[str]`
- Pipeline formatter handles multi-step when/then lists
- Agent prompts updated with traceability fields and array schema

---

### 🔲 Phase 2 — Browser Intelligence (NEXT)
> Issues #26–30 · Priority: High

| Issue | Title | Status |
|-------|-------|--------|
| #26 | Browser profile management (persist cookies/session) | 🔲 Open |
| #27 | Browser skills library (reusable action sequences) | 🔲 Open |
| #28 | Browser judge mode (self-evaluating execution) | 🔲 Open |
| #29 | Session keep-alive / CDP reconnect | 🔲 Open |
| #30 | Two-phase Gherkin (plan → refine after DOM inspection) | 🔲 Open |

---

### 🔲 Phase 3 — Element Intelligence
> Issues #31–33

| Issue | Title | Status |
|-------|-------|--------|
| #31 | A11y + security + visual + performance element analysis | 🔲 Open |
| #32 | Interactive element selection UI | 🔲 Open |
| #33 | DOM proxy / element observatory | 🔲 Open |

---

### 🔲 Phase 4 — Persistence + Observability
> Issues #34–36

| Issue | Title | Status |
|-------|-------|--------|
| #34 | SSE streaming for real-time pipeline progress | 🔲 Open |
| #35 | Run history + test result storage | 🔲 Open |
| #36 | Analytics dashboard | 🔲 Open |

---

### 🔲 Phase 5 — Platform
> Issues #37–41

| Issue | Title | Status |
|-------|-------|--------|
| #37 | SiteScout — autonomous site exploration agent | 🔲 Open |
| #38 | Multi-LLM per agent (different model per stage) | 🔲 Open |
| #39 | Agent Builder UI (visual agent configuration) | 🔲 Open |
| #40 | Test Strategy Generator | 🔲 Open |
| #41 | Confidential mode / Ollama-only local execution | 🔲 Open |

---

### 🔲 Production Readiness
> Issues #19–21

| Issue | Title | Status |
|-------|-------|--------|
| #19 | Docker Compose full-stack setup | 🔲 Open |
| #20 | Rate limiting on all endpoints | 🔲 Open |
| #21 | Groq provider integration | 🔲 Open |

---

## Known Technical Debt

| ID | Issue | Severity | Phase to Fix |
|----|-------|----------|--------------|
| H1 | Sync blocking calls inside async endpoints (`test_case_service`, `gherkin_service`) | High | Phase 2 |
| C1 | CORS wildcard + `credentials=True` in main.py | High | Phase 4 |
| C2 | `--disable-web-security` Chrome flag in browser agent | Medium | Phase 2 |
| QA1 | No unit tests for core services | High | Phase 4 |

---

## PR History

| PR | Title | Merged |
|----|-------|--------|
| #42 | Phase 1 intelligence core (issues #22–25) | 2026-03-15 |
| #50 | Security hardening + model correctness | 2026-03-16 |

---

## How to Update This File

When a phase issue is closed:
1. Change `🔲 Open` → `✅ Done` in the relevant table
2. Update the "Current Status" table at the top
3. Add a row to "PR History" when a PR merges

When new technical debt is found:
- Add a row to the Technical Debt table with a severity and target phase
