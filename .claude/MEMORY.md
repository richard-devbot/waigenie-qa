# MEMORY.md — WAIGenie Project Memory Index

This is the project-level memory index for the `waigenie` repository.
It provides Claude Code with persistent context across sessions.

---

## Quick Reference

| File | Purpose |
|------|---------|
| [CLAUDE.md](CLAUDE.md) | Project instructions, conventions, architecture rules |
| [AGENTS.md](AGENTS.md) | All 5 agent definitions, schemas, routes |
| [HEARTBEAT.md](HEARTBEAT.md) | Phase tracker, open issues, technical debt |

---

## Project Identity

- **Repo:** https://github.com/richard-devbot/waigenie-qa
- **Local path:** `/mnt/d/SDET-GENIE/waigenie`
- **Part of:** SDET-GENIE monorepo workspace (`/mnt/d/SDET-GENIE`)
- **Stack:** FastAPI + Agno + browser-use + Next.js 14 + LanceDB
- **Remotes:** `origin` (personal), `richard` (richard-devbot org)

---

## Active Development Context

**Current main:** `828fde4` — PR #50 merged (security hardening + model correctness)

**Next work:** Phase 2 Browser Intelligence (#26–30)
- Start with issue #26 (browser profile management) or #29 (session keep-alive)
- Branch from `main` as `feature/26-browser-profiles`

**Sync command (keep waigenie up to date):**
```bash
git pull richard main
```

---

## Architectural Decisions (ADRs)

### ADR-001: Pydantic structured outputs for all agents
All 5 agents use `response_model=` with strict Pydantic v2 models. No free-form text parsing.
Adopted in Phase 1 (issue #22).

### ADR-002: List[str] for all Gherkin step fields
`GherkinScenario.given/when/then` are `List[str]`. Never `Union[str, List[str]]` or bare `str`.
Enforced in PR #50 (issue #46).

### ADR-003: secrets.compare_digest for API key validation
All key comparisons use `secrets.compare_digest()` to prevent timing attacks.
Enforced in PR #50 (issue #43).

### ADR-004: No tracebacks in API responses
Exceptions are logged server-side with `exc_info=True`. API responses contain only `str(e)`.
Enforced in PR #50 (issue #44).

### ADR-005: Agent prompts as markdown files
Agent instructions live in `backend/app/prompts/*.md`, loaded at runtime.
This allows prompt iteration without code changes.

---

## Session Notes

> Add notes here for context that should persist across Claude Code sessions.
> Format: `YYYY-MM-DD: <note>`

- 2026-03-15: Phase 1 merged (PR #42). Code review found C1/C2/C3/C4/H1/QA1/QA3 issues.
- 2026-03-16: PR #50 merged. Fixed all 5 qodo review findings. `.claude` folder created.
