# AGENTS.md — WAIGenie AI Agent Documentation

This file documents all 5 Agno-powered agents in the WAIGenie framework.
Each agent has a dedicated service, prompt file, and Pydantic output model.

---

## Agent Overview

```
┌─────────────────────────────────────────────────────────┐
│                    QA Master Orchestrator               │
│              (Agno Team — coordinate mode)              │
│                     orchestrator.py                     │
└─────────┬──────────────┬───────────────┬───────────────┘
          │              │               │
    ┌─────▼──────┐  ┌────▼──────┐  ┌────▼──────────┐
    │ StoryForge │  │ TestCraft │  │  GherkinGen   │
    │  (story)   │  │  (tests)  │  │  (gherkin)    │
    └────────────┘  └─────┬─────┘  └──────┬────────┘
                          │               │
                    ┌─────▼───────────────▼──────┐
                    │      Agno Workflow 2.0      │
                    │   (parallel TestCraft +     │
                    │      GherkinGen)            │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │       BrowserAgent          │
                    │   (Playwright/CDP/CDP)      │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │        CodeSmith            │
                    │  (Selenium/Playwright/      │
                    │       Cypress code)         │
                    └─────────────────────────────┘
```

---

## Agent 1: StoryForge

**Purpose:** Enhance raw user stories into structured, testable specifications.

| Property | Value |
|----------|-------|
| File | `backend/app/agents/user_story_agent.py` |
| Prompt | `backend/app/prompts/user_story_agent_instructions.md` |
| Output model | `EnhancedStory` |
| Service | `backend/app/services/story_service.py` |
| Route | `POST /api/v1/story/enhance` |

**Output fields:**
- `title`, `as_a`, `i_want`, `so_that`, `elaboration`
- `acceptance_criteria: List[str]`
- `implementation_notes: List[str]`
- `testability_considerations: List[str]`
- `related_stories: List[str]`

---

## Agent 2: TestCraft

**Purpose:** Convert enhanced user stories into comprehensive manual test cases.

| Property | Value |
|----------|-------|
| File | `backend/app/agents/test_case_agent.py` |
| Prompt | `backend/app/prompts/test_case_agent_instructions.md` |
| Output model | `TestCaseList` → `TestCase` |
| Service | `backend/app/services/test_case_service.py` |
| Route | `POST /api/v1/tests/generate` |

**Output fields (TestCase):**
- `id`, `title`, `description`, `pre_conditions`
- `steps: List[str]`, `expected_results: List[str]`
- `test_data`, `priority`, `test_type`, `status`
- `post_conditions`, `environment`, `automation_status`
- **Traceability:** `user_story_id`, `acceptance_criterion_ref`, `tags: List[str]`, `severity`

**Coverage requirements per acceptance criterion:**
Happy path, negative, boundary min/max, boundary violation, empty/null, special chars, concurrent/state.

---

## Agent 3: GherkinGen

**Purpose:** Convert manual test cases into executable Gherkin `.feature` scenarios.

| Property | Value |
|----------|-------|
| File | `backend/app/agents/gherkin_agent.py` |
| Prompt | `backend/app/prompts/gherkin_agent_instructions.md` |
| Output model | `GherkinFeature` → `GherkinScenario` |
| Service | `backend/app/services/gherkin_service.py` |
| Route | `POST /api/v1/gherkin/generate` |

**Output fields (GherkinScenario):**
- `title`, `feature`, `background`, `entry_point_url`
- `tags: List[str]`
- `given: List[str]` — precondition steps (MUST start with real URL)
- `when: List[str]` — action steps (one user action = one scenario)
- `then: List[str]` — DOM-assertable outcome steps
- `and_steps: List[str]` (alias: `and`), `but: str`

**Critical schema rule:** `given/when/then` are ALWAYS `List[str]`, never bare strings.

---

## Agent 4: BrowserAgent

**Purpose:** Execute Gherkin scenarios against a live browser using Playwright + CDP.

| Property | Value |
|----------|-------|
| File | `backend/app/agents/browser_execution_agent.py` |
| Prompt | `backend/app/prompts/browser_execution_agent_instructions.md` |
| Output model | `BrowserExecutionResult` → `ScenarioResult` → `StepResult` |
| Service | `backend/app/services/browser_execution_service.py` |
| Route | `POST /api/v1/execute` |

**Output fields (BrowserExecutionResult):**
- `results: List[ScenarioResult]`
- `total_scenarios`, `passed`, `failed`, `raw_response`

**Execution modes:**
- Parallel execution (default) via MCP service job queue
- CDP attach mode: connect to existing Chrome via `cdp_port`
- Vision mode: screenshot-based element detection

---

## Agent 5: CodeSmith

**Purpose:** Generate production-ready automation code from Gherkin + browser execution history.

| Property | Value |
|----------|-------|
| File | `backend/app/agents/code_generation_agent.py` |
| Prompt | `backend/app/prompts/code_generation_agent_instructions.md` |
| Output model | `GeneratedCode` |
| Service | `backend/app/services/code_generation_service.py` |
| Route | `POST /api/v1/code/generate` |

**Output fields:**
- `framework` (Selenium/Playwright/Cypress)
- `language`, `code`, `file_name`
- `imports: List[str]`, `notes`

**Supported frameworks:** Selenium (Python), Playwright (Python/JS), Cypress (JS)

---

## Orchestration Layer

### QA Pipeline (sequential, 5-stage)
- File: `backend/app/services/pipeline_service.py`
- Route: `POST /api/v1/pipeline/start`
- Returns: `task_id` — poll `GET /api/v1/pipeline/status/{task_id}` for progress

### Agno Workflow 2.0 (parallel TestCraft + GherkinGen)
- File: `backend/app/workflows/qa_pipeline.py`
- Route: `POST /api/v1/pipeline/workflow`
- Runs TestCraft and GherkinGen in parallel, then sequential browser + code stages

### QA Master Orchestrator (Team coordinate mode)
- File: `backend/app/agents/orchestrator.py`
- Route: `POST /api/v1/pipeline/orchestrate`
- Uses Agno Team with a coordinator agent routing tasks to sub-agents

---

## Adding a New Agent

1. `backend/app/agents/<name>_agent.py` — `create_<name>_agent()` factory
2. `backend/app/prompts/<name>_agent_instructions.md` — instructions loaded at runtime
3. `backend/app/models/agent_outputs.py` — Pydantic output model
4. `backend/app/services/<name>_service.py` — business logic
5. `backend/app/api/v1/<name>.py` — FastAPI route with `Depends(verify_api_key)`
6. Wire into `pipeline_service.py` if it belongs in the main pipeline
