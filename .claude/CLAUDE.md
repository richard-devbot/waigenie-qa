# CLAUDE.md — WAIGenie QA Automation Framework

This file provides guidance to Claude Code when working in the `waigenie` repository.
It is the **single source of truth** for project context, conventions, and development rules.

---

## Project Overview

WAIGenie is an AI-powered QA automation framework that automates the full SDET workflow:

```
User Story → Test Cases → Gherkin Scenarios → Browser Execution → Automation Code
```

**Stack:**
- Backend: FastAPI + Python 3.11 + Agno framework
- Agents: browser-use (Playwright/CDP) + LanceDB vector memory
- Frontend: Next.js 14
- LLMs: Gemini, OpenAI, Anthropic, Groq, Ollama (multi-provider)

---

## Repository Structure

```
waigenie/
  backend/
    app/
      agents/          # 5 Agno AI agents (see AGENTS.md)
      api/v1/          # FastAPI route handlers
      config/          # Settings (pydantic-settings + .env)
      models/          # Pydantic structured output models
      prompts/         # Agent instruction markdown files
      services/        # Business logic layer
      utils/           # Shared utilities (model_factory, task_manager)
      workflows/       # Agno Workflow 2.0 (parallel execution)
  frontend/            # Next.js 14 UI
  .claude/             # Claude Code project config (this folder)
```

---

## The 5 Agents

See **AGENTS.md** for full documentation.

| Agent | Service | Route |
|-------|---------|-------|
| StoryForge | `story_service.py` | `POST /api/v1/story/enhance` |
| TestCraft | `test_case_service.py` | `POST /api/v1/tests/generate` |
| GherkinGen | `gherkin_service.py` | `POST /api/v1/gherkin/generate` |
| BrowserAgent | `browser_execution_service.py` | `POST /api/v1/execute` |
| CodeSmith | `code_generation_service.py` | `POST /api/v1/code/generate` |

The full pipeline (all 5 in sequence) runs via `POST /api/v1/pipeline/start`.

---

## Key Architecture Rules

### Models (`backend/app/models/agent_outputs.py`)
- All agent outputs are **Pydantic v2 structured models** with `response_model=` on the Agno agent
- `GherkinScenario.given/when/then` are `List[str]` — never bare strings
- `TestCase` includes traceability fields: `user_story_id`, `acceptance_criterion_ref`, `tags`, `severity`

### Agent Prompts (`backend/app/prompts/*.md`)
- Each agent has a `*_agent_instructions.md` file loaded at runtime via `load_agent_instructions()`
- Prompt changes immediately affect agent output — no restart needed
- All prompts must be consistent with the Pydantic model schema

### Authentication (`backend/app/api/deps.py`)
- `verify_api_key` dependency applied to all pipeline/execute routes
- Uses `secrets.compare_digest()` — never plain `==` for key comparison
- `API_KEY_REQUIRED=False` by default (dev mode); set `True` + unique `SECRET_KEY` for production
- Startup raises `ValueError` if `API_KEY_REQUIRED=True` with default key

### Error Handling (`backend/app/services/pipeline_service.py`)
- All exceptions are logged with `exc_info=True` — no raw tracebacks in API responses
- Pipeline errors return `{"status": "FAILED", "message": str(e)}` — never `traceback.format_exc()`

### Async Rules
- All service layer methods called from async endpoints must themselves be `async def`
- Never use `time.sleep()` inside async code — use `await asyncio.sleep()`
- `pipeline_service.py` uses `asyncio.create_task()` for background pipeline execution

---

## Development Workflow

### Running locally
```bash
# Backend
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm run dev
```

### Adding a new agent
1. Create `backend/app/agents/<name>_agent.py` — define `create_<name>_agent()`
2. Create `backend/app/prompts/<name>_agent_instructions.md` — agent instructions
3. Add Pydantic output model to `backend/app/models/agent_outputs.py`
4. Create `backend/app/services/<name>_service.py` — business logic
5. Wire into `backend/app/api/v1/<name>.py` — FastAPI route
6. Update `AGENTS.md` with documentation

### Changing agent prompts
Edit `backend/app/prompts/<agent>_agent_instructions.md` directly.
The `load_agent_instructions()` utility reads these at agent creation time.

### Adding a new LLM provider
Edit `backend/app/utils/model_factory.py` — add the new provider to `get_llm_instance()`.

---

## Phase Roadmap

See **HEARTBEAT.md** for current phase status and open issues.

| Phase | Issues | Theme | Status |
|-------|--------|-------|--------|
| Phase 1 | #22–25 | Intelligence Core (Pydantic, ReasoningTools, Workflow, Team) | ✅ Done |
| Phase 2 | #26–30 | Browser Intelligence | 🔲 Next |
| Phase 3 | #31–33 | Element Intelligence | 🔲 Planned |
| Phase 4 | #34–36 | Persistence + Observability | 🔲 Planned |
| Phase 5 | #37–41 | Platform + Multi-LLM | 🔲 Planned |
| Production | #19–21 | Docker, Rate Limiting, Groq | 🔲 Planned |

---

## Conventions

- **Branch naming**: `feature/<issue#>-short-desc`, `fix/<issue#>-short-desc`
- **Commit format**: `type(scope): message` — e.g. `feat(#26): add browser profiles`
- **PR reviews**: All PRs go through qodo-code-review bot; address all findings before merge
- **No raw secrets** in code — always read from `settings.*` (populated from `.env`)
- **No `Union[str, List[str]]`** for step fields — always enforce `List[str]`
