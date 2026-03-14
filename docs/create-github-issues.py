#!/usr/bin/env python3
"""
WAIGenie Enhancement GitHub Issues Creator
Creates enhancement issues combining best features from SDET-GENIE + QA-SDET into WAIGenie.

Usage:
    python docs/create-github-issues.py --token YOUR_GITHUB_TOKEN
    python docs/create-github-issues.py --token YOUR_TOKEN --repo richard-devbot/waigenie
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error

def create_issue(token: str, repo: str, title: str, body: str, labels: list[str]) -> dict:
    url = f"https://api.github.com/repos/{repo}/issues"
    data = json.dumps({"title": title, "body": body, "labels": labels}).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"  OK #{result['number']}: {result['title']}")
            return result
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        print(f"  FAIL {title}: {e.code} {body_text[:200]}")
        return {}


def create_label(token: str, repo: str, name: str, color: str, description: str = "") -> None:
    url = f"https://api.github.com/repos/{repo}/labels"
    data = json.dumps({"name": name, "color": color, "description": description}).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"  Created label: {name}")
    except urllib.error.HTTPError as e:
        if e.code == 422:
            print(f"  Label exists: {name}")
        else:
            print(f"  FAIL label {name}: {e.code}")


def main():
    parser = argparse.ArgumentParser(description="Create WAIGenie enhancement issues on GitHub")
    parser.add_argument("--token", required=True, help="GitHub personal access token (needs repo scope)")
    parser.add_argument("--repo", default="WaiGenie/waigenie", help="GitHub repo (default: WaiGenie/waigenie)")
    args = parser.parse_args()

    TOKEN = args.token
    REPO = args.repo

    # ── Labels ──────────────────────────────────────────────────────────────
    print(f"\n=== Creating Labels on {REPO} ===")
    labels = [
        ("backend", "0075ca", "Backend Python/FastAPI"),
        ("frontend", "e4e669", "Frontend Next.js/TypeScript"),
        ("intelligence", "d93f0b", "AI/ML/Memory/KB"),
        ("browser", "0e8a16", "Browser automation"),
        ("streaming", "5319e7", "SSE / real-time"),
        ("integrations", "f9d0c4", "External integrations"),
        ("production", "b60205", "Production hardening"),
        ("enhancement", "a2eeef", "New feature or improvement"),
        ("from-sdet-genie", "c2e0c6", "Ported from SDET-GENIE"),
        ("from-qa-sdet", "bfdadc", "Ported from QA-SDET"),
        ("new-feature", "0052cc", "Net-new capability"),
    ]
    for name, color, desc in labels:
        create_label(TOKEN, REPO, name, color, desc)
        time.sleep(0.3)

    issues = []

    # ── Backend: Intelligence (Memory + KB + Self-Evolution) ──────────────
    print("\n=== Backend: Intelligence Layer ===")

    issues.append(create_issue(TOKEN, REPO,
        "[BE-1] Add Agno Memory V2 — persistent user context across sessions",
        """## Summary
Integrate Agno Memory V2 (`agno.memory.v2`) into WAIGenie so agents remember user preferences, past test patterns, and application context across sessions.

## Why
Currently each pipeline run starts from scratch. With Memory V2, agents recall:
- Which selectors worked for a given app
- User's preferred test frameworks (Playwright vs Selenium)
- Previously enhanced stories for the same feature

## Implementation
- Add `SqliteMemoryDb` as default (upgrade to `PostgresMemoryDb` when PostgreSQL configured)
- Inject `Memory` instance into all 5 agents via `memory=` parameter
- Store: user_id (from session), past_runs summary, preferred frameworks
- Expose `GET /api/v1/memory` to let frontend show remembered context

## Files to touch
- `backend/app/intelligence/memory.py` (new)
- `backend/app/agents/*.py` — add `memory=` param
- `backend/app/api/v1/memory.py` (new endpoint)
- `backend/app/config/settings.py` — add `MEMORY_DB_FILE`

## Acceptance Criteria
- [ ] Second run for same app recalls selector patterns from first run
- [ ] Memory persists across server restarts
- [ ] Frontend can display "I remember this app" context indicator""",
        ["backend", "intelligence", "enhancement", "from-sdet-genie"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[BE-2] Add LanceDB Knowledge Base — store verified test patterns",
        """## Summary
Add a LanceDB vector knowledge base to WAIGenie for storing and retrieving verified test patterns, working selectors, and reusable test strategies.

## Why
When browser execution succeeds, the working selectors and UI patterns are valuable. Storing them in a KB allows:
- Future runs to start with known-good selectors
- Code generation to use proven patterns
- Skill sharing across different apps with similar UI patterns

## Implementation
- `backend/app/intelligence/knowledge_base.py` — `QAKnowledgeBase` class wrapping `AgentKnowledge`
- LanceDB as default (zero-infra), PgVector for production
- Collections: `selectors`, `ui_patterns`, `test_strategies`, `gherkin_templates`
- `GET /api/v1/knowledge/search?q=` — semantic search endpoint
- `POST /api/v1/knowledge` — add entry
- `DELETE /api/v1/knowledge/{id}` — remove entry

## Files to touch
- `backend/app/intelligence/knowledge_base.py` (new)
- `backend/app/api/v1/knowledge.py` (new)
- `backend/app/config/settings.py` — add `LANCEDB_URI`
- `backend/requirements.txt` — add `lancedb`

## Acceptance Criteria
- [ ] KB initializes on startup with LanceDB
- [ ] Semantic search returns relevant patterns
- [ ] Verified selectors from browser runs are stored automatically""",
        ["backend", "intelligence", "enhancement", "from-sdet-genie"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[BE-3] Self-evolution loop — post-run learning from every execution",
        """## Summary
After each successful browser execution, automatically extract working selectors and UI patterns and save them to the Knowledge Base and Memory V2.

## Why
This is the core differentiator — WAIGenie improves with every run. The "self-evolving" agent mechanism means:
- Selectors that work get stored and reused
- Failed selectors are flagged and avoided
- Code generation improves over time

## Implementation
```python
# After BrowserPilot completes successfully:
async def evolve_from_run(run_result: RunResult, kb: QAKnowledgeBase, memory: Memory):
    # 1. Extract successful element interactions from ElementTracker
    for interaction in run_result.element_tracker.get_interactions():
        selectors = interaction["element_details"]["selectors"]
        kb.add_selector(url=run_result.url, selectors=selectors)

    # 2. Extract Gherkin → selector mappings
    for scenario in run_result.gherkin_scenarios:
        pattern = extract_ui_pattern(scenario, run_result.element_tracker)
        kb.add_pattern(pattern)

    # 3. Update Memory with run summary
    memory.add_message(user_id=run_result.user_id, message=run_summary)
```

## Files to touch
- `backend/app/intelligence/evolution.py` (new)
- `backend/app/services/pipeline_service.py` — call evolve_from_run after browser step
- `backend/app/api/v1/pipeline.py` — include evolution status in response

## Acceptance Criteria
- [ ] After a successful run, selectors are in the KB
- [ ] Second run for same app is faster/more accurate (uses KB context)
- [ ] Failed selectors are marked in KB with low confidence score""",
        ["backend", "intelligence", "enhancement", "new-feature"]
    ))
    time.sleep(0.5)

    # ── Backend: Agent Improvements ───────────────────────────────────────
    print("\n=== Backend: Agent Improvements ===")

    issues.append(create_issue(TOKEN, REPO,
        "[BE-4] Structured Pydantic outputs for all 5 agents",
        """## Summary
Replace free-form markdown responses from all 5 agents with strongly-typed Pydantic response models using Agno's `response_model=` parameter.

## Why
Currently agents return markdown strings that the frontend parses with regex. Structured outputs:
- Eliminate parsing fragility
- Enable the frontend to render rich structured data
- Allow downstream agents to consume structured input from upstream agents

## Pydantic Models to Create
```python
class EnhancedStory(BaseModel):
    title: str
    as_a: str
    i_want: str
    so_that: str
    acceptance_criteria: list[str]
    implementation_notes: list[str]
    testability_notes: list[str]
    jira_ticket_id: str | None

class TestCase(BaseModel):
    id: str
    title: str
    type: Literal["positive", "negative", "edge", "boundary"]
    preconditions: list[str]
    steps: list[str]
    expected_result: str
    priority: Literal["high", "medium", "low"]

class GherkinFeature(BaseModel):
    feature_name: str
    background: str | None
    scenarios: list[GherkinScenario]

class GeneratedCode(BaseModel):
    framework: str
    language: str
    code: str
    imports: list[str]
    page_object: str | None
    helper_functions: list[str]
```

## Files to touch
- `backend/app/models/agent_outputs.py` (new — all Pydantic models)
- `backend/app/agents/*.py` — add `response_model=` param
- `backend/app/api/v1/*.py` — update response schemas

## Acceptance Criteria
- [ ] All 5 agents return structured Pydantic objects
- [ ] Frontend can destructure fields directly (no regex parsing)
- [ ] Type errors caught at runtime before returning to client""",
        ["backend", "enhancement", "from-sdet-genie"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[BE-5] Add Ollama local model support to model factory",
        """## Summary
Extend `model_factory.py` and the Settings to support Ollama (local models: llama3.2, gemma3, qwen2.5, mistral, codellama).

## Why
- Free, offline, privacy-preserving testing
- Teams with strict data governance policies can use local models
- Great for development without burning API credits

## Implementation
```python
# In SUPPORTED_MODELS:
"Ollama": {
    "api_key_env": None,  # No key needed
    "base_url_env": "OLLAMA_BASE_URL",
    "models": {
        "llama3.2": {"agno_class": AgnoOllama, "browser_use_class": ChatOllama},
        "gemma3": {"agno_class": AgnoOllama, "browser_use_class": ChatOllama},
        "qwen2.5": {"agno_class": AgnoOllama, "browser_use_class": ChatOllama},
        "codellama": {"agno_class": AgnoOllama, "browser_use_class": ChatOllama},
        "mistral": {"agno_class": AgnoOllama, "browser_use_class": ChatOllama},
    }
}
```

## Files to touch
- `backend/app/utils/model_factory.py` — add Ollama provider
- `backend/app/config/settings.py` — add `OLLAMA_BASE_URL`
- `backend/app/api/v1/pipeline.py` — add Ollama to provider dropdown data
- `backend/.env.example` — add `OLLAMA_BASE_URL=http://localhost:11434`
- `frontend/app/dashboard/settings/page.tsx` — add Ollama section

## Acceptance Criteria
- [ ] Ollama provider selectable in pipeline settings
- [ ] Pipeline runs fully with local llama3.2 model
- [ ] Graceful error if Ollama not running (not crash)""",
        ["backend", "enhancement", "new-feature"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[BE-6] SSE streaming endpoint — real-time pipeline events to frontend",
        """## Summary
Add a Server-Sent Events (SSE) endpoint so the frontend receives live updates during pipeline execution: agent activated, tool calls, browser screenshots, step completions, errors.

## Why
Currently the frontend polls or waits for the full pipeline to complete. SSE gives:
- Real-time "Agent X is thinking..." feedback
- Live browser screenshot streaming during execution
- Immediate error visibility without waiting for full run

## Implementation
```python
# backend/app/api/v1/stream.py
from fastapi.responses import StreamingResponse
import asyncio, json

@router.get("/stream/{run_id}")
async def stream_pipeline(run_id: str):
    async def event_generator():
        queue = get_run_queue(run_id)
        while True:
            event = await queue.get()
            yield f"data: {json.dumps(event)}\\n\\n"
            if event["type"] == "complete": break
    return StreamingResponse(event_generator(), media_type="text/event-stream")

# Event types: agent_start, agent_complete, tool_call, browser_screenshot,
#              browser_step, error, complete
```

## Files to touch
- `backend/app/api/v1/stream.py` (new)
- `backend/app/services/pipeline_service.py` — emit events to queue
- `backend/app/agents/*.py` — emit agent lifecycle events
- `frontend/app/dashboard/pipeline/page.tsx` — connect to SSE

## Acceptance Criteria
- [ ] Frontend updates in real-time without polling
- [ ] Each agent activation shows in UI as it happens
- [ ] Browser screenshots stream live to frontend
- [ ] Errors show immediately""",
        ["backend", "frontend", "streaming", "enhancement", "new-feature"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[BE-7] Run history — persist and retrieve all pipeline runs",
        """## Summary
Save every pipeline run to SQLite (or PostgreSQL) so users can browse past runs, replay artifacts, and compare results over time.

## Implementation
```python
class PipelineRun(Base):
    __tablename__ = "pipeline_runs"
    id: str  # UUID
    created_at: datetime
    user_story_input: str
    url: str | None
    model_provider: str
    model_name: str
    framework: str
    status: Literal["running", "completed", "failed"]
    enhanced_story: dict | None
    test_cases: list | None
    gherkin_scenarios: list | None
    artifacts: dict | None  # paths to video, HAR, GIF
    duration_seconds: float | None
    error_message: str | None
```

## Endpoints
- `GET /api/v1/runs` — list all runs (paginated)
- `GET /api/v1/runs/{run_id}` — get run detail
- `DELETE /api/v1/runs/{run_id}` — delete a run
- `GET /api/v1/runs/{run_id}/artifacts` — download artifacts

## Files to touch
- `backend/app/db/models.py` (new)
- `backend/app/db/session.py` (new)
- `backend/app/api/v1/runs.py` (new)
- `backend/app/services/pipeline_service.py` — save run on start/complete

## Acceptance Criteria
- [ ] Every pipeline run is persisted
- [ ] Run history page shows past 50 runs
- [ ] Clicking a run shows full results + artifacts""",
        ["backend", "enhancement", "new-feature"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[BE-8] Agno Team orchestration — coordinate agents as a Team",
        """## Summary
Wrap the 5 pipeline agents in an Agno `Team` with `TeamMode.coordinate` mode so the Master Orchestrator can intelligently route tasks, handle failures, and coordinate parallel execution.

## Why (from SDET-GENIE design)
- Story + Test + Gherkin can run in parallel with `Parallel()` step
- Team can retry failed agents with different models
- Orchestrator has full context of all agent outputs

## Implementation
```python
from agno.team import Team
from agno.team.team import TeamMode

qa_team = Team(
    name="QA Orchestrator",
    mode=TeamMode.coordinate,
    model=orchestrator_model,
    members=[story_agent, test_agent, gherkin_agent, browser_agent, code_agent],
    instructions="Orchestrate the QA pipeline..."
)
```

## Files to touch
- `backend/app/agents/orchestrator.py` (new)
- `backend/app/services/pipeline_service.py` — use Team instead of sequential calls
- `backend/requirements.txt` — verify agno version supports Teams

## Acceptance Criteria
- [ ] All agents run as part of Agno Team
- [ ] Story enhancement runs first, then Test+Gherkin in parallel
- [ ] Browser execution runs after Gherkin completes""",
        ["backend", "intelligence", "enhancement", "from-sdet-genie"]
    ))
    time.sleep(0.5)

    # ── Backend: Integrations ─────────────────────────────────────────────
    print("\n=== Backend: Integrations ===")

    issues.append(create_issue(TOKEN, REPO,
        "[BE-9] Enhanced Jira integration — create test cycles + update results",
        """## Summary
Extend the existing Jira integration (JiraTools in user_story_agent) to support: creating test cycles, attaching generated test cases, and updating execution results after browser runs.

## From QA-SDET
QA-SDET had Jira fetch+write. Port that approach into WAIGenie's FastAPI structure.

## New Capabilities
- Fetch Jira ticket → auto-populate story input
- Create Jira test cycle from generated test cases
- Update Jira issue with test execution results
- Link Gherkin scenarios to Jira test cases

## Endpoints
- `POST /api/v1/jira/fetch` — fetch ticket by ID
- `POST /api/v1/jira/create-test-cycle` — create test cycle
- `POST /api/v1/jira/update-results` — update with execution results

## Files to touch
- `backend/app/services/jira_service.py` (new — expanded beyond JiraTools)
- `backend/app/api/v1/jira.py` (new)
- `frontend/app/dashboard/pipeline/components/input/PipelineInput.tsx` — add Jira ticket input

## Acceptance Criteria
- [ ] Enter Jira ticket ID → story auto-populated from Jira
- [ ] Generated test cases create a Jira test cycle
- [ ] After browser execution → Jira issue updated with pass/fail""",
        ["backend", "integrations", "enhancement", "from-qa-sdet"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[BE-10] Linear integration — fetch issues + update with test results",
        """## Summary
Add Linear integration using Agno's built-in `LinearTools`. Fetch Linear issues as story input, create test cycles, and update issue status after execution.

## Implementation
```python
from agno.tools.linear_app import LinearTools

linear_tools = LinearTools(api_key=settings.LINEAR_API_KEY)
# Tools available: search_issues, get_issue, update_issue, create_issue
```

## Endpoints
- `POST /api/v1/linear/fetch` — fetch Linear issue
- `POST /api/v1/linear/update` — update issue with test results

## Files to touch
- `backend/app/services/linear_service.py` (new)
- `backend/app/api/v1/linear.py` (new)
- `backend/app/config/settings.py` — add `LINEAR_API_KEY`
- `backend/.env.example` — add LINEAR_API_KEY

## Acceptance Criteria
- [ ] Enter Linear issue ID → story auto-populated
- [ ] After pipeline run → Linear issue updated""",
        ["backend", "integrations", "enhancement", "new-feature"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[BE-11] SiteScout Agent — crawl URL and auto-generate test skills",
        """## Summary
New agent that takes a URL, crawls the application using browser-use, identifies all UI components and interaction patterns, and stores reusable test skills in the Knowledge Base.

## From SDET-GENIE concept
SDET-GENIE designed this as a way to bootstrap the KB for a new app. One SiteScout run generates dozens of skills.

## Skills Generated
- Login flow pattern
- Form submission patterns
- Navigation patterns
- Modal/dialog patterns
- Table interaction patterns

## Implementation
```python
class SiteScoutAgent:
    async def scout(self, url: str) -> list[TestSkill]:
        browser_agent = create_browser_use_agent(model)
        result = await browser_agent.run(f"Explore {url} and map all UI interactions")
        skills = extract_skills_from_execution(result, element_tracker)
        kb.bulk_add_skills(skills)
        return skills
```

## Endpoints
- `POST /api/v1/scout` — start scouting a URL
- `GET /api/v1/scout/{task_id}` — get scouting status + skills found

## Files to touch
- `backend/app/agents/site_scout_agent.py` (new)
- `backend/app/api/v1/scout.py` (new)

## Acceptance Criteria
- [ ] Given a URL, SiteScout identifies 5+ reusable UI patterns
- [ ] Skills stored in KB with appropriate tags
- [ ] Subsequent pipeline runs for same app use discovered skills""",
        ["backend", "intelligence", "browser", "enhancement", "new-feature"]
    ))
    time.sleep(0.5)

    # ── Frontend Enhancements ─────────────────────────────────────────────
    print("\n=== Frontend Enhancements ===")

    issues.append(create_issue(TOKEN, REPO,
        "[FE-1] Real-time SSE streaming UI — live pipeline progress with agent graph",
        """## Summary
Update the pipeline page to connect to the SSE endpoint and show real-time agent progress: which agent is running, what it's doing, live browser screenshots streaming in.

## UI Components
- Agent graph: 5 nodes (Story → Test+Gherkin parallel → Browser → Code)
- Each node shows: pending / running (spinner) / done (check) / failed (X)
- Live log panel below: "TestCraft Agent activated", "Browser navigating to..."
- Live screenshot panel: updates in real-time during browser execution

## Implementation
```typescript
// useSSEPipeline hook
const useSSEPipeline = (runId: string) => {
  const [events, setEvents] = useState<PipelineEvent[]>([]);
  useEffect(() => {
    const source = new EventSource(`/api/v1/stream/${runId}`);
    source.onmessage = (e) => setEvents(prev => [...prev, JSON.parse(e.data)]);
    return () => source.close();
  }, [runId]);
  return events;
};
```

## Files to touch
- `frontend/app/hooks/useSSEPipeline.ts` (new)
- `frontend/app/dashboard/pipeline/components/visualizer/PipelineVisualizer.tsx` — add live status
- `frontend/app/dashboard/pipeline/page.tsx` — connect SSE hook

## Acceptance Criteria
- [ ] Agent nodes update in real-time
- [ ] Log panel shows live messages
- [ ] Browser screenshots update during execution""",
        ["frontend", "streaming", "enhancement", "new-feature"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[FE-2] Run history page — browse past pipeline runs with replay",
        """## Summary
New `/dashboard/history` page showing all past pipeline runs with ability to view full results, download artifacts, and rerun with same settings.

## UI Layout
- Table: Date | Story | URL | Model | Status | Duration | Actions
- Click row → expand to show full run detail (same as current pipeline results)
- Download button for each artifact (video, HAR, GIF, code)
- Rerun button: pre-fills pipeline input with original settings
- Delete button: remove run and artifacts

## Files to touch
- `frontend/app/dashboard/history/page.tsx` (new)
- `frontend/app/dashboard/history/components/RunTable.tsx` (new)
- `frontend/app/dashboard/history/components/RunDetail.tsx` (new)
- `frontend/lib/api.ts` — add runs API functions
- `frontend/app/layout/Sidebar.tsx` — add History link

## Acceptance Criteria
- [ ] All past runs listed with pagination (20 per page)
- [ ] Click run → see full results
- [ ] Download artifacts works
- [ ] Rerun pre-fills the pipeline form""",
        ["frontend", "enhancement", "new-feature"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[FE-3] Knowledge Explorer — browse, search, and manage the KB",
        """## Summary
New `/dashboard/knowledge` page to browse and search the LanceDB knowledge base. View stored selectors, UI patterns, test strategies. Add manual entries. Delete stale entries.

## UI Layout
- Search bar (semantic search → calls `GET /api/v1/knowledge/search`)
- Filter tabs: All | Selectors | UI Patterns | Gherkin Templates | Skills
- Card grid: each card shows entry content, metadata, confidence score, last used date
- Add button: form to add manual knowledge entry
- Delete button per card
- "From run #X" link to trace where knowledge came from

## Files to touch
- `frontend/app/dashboard/knowledge/page.tsx` (new)
- `frontend/app/dashboard/knowledge/components/KnowledgeCard.tsx` (new)
- `frontend/app/dashboard/knowledge/components/SearchBar.tsx` (new)
- `frontend/lib/api.ts` — add knowledge API functions
- `frontend/app/layout/Sidebar.tsx` — add Knowledge link

## Acceptance Criteria
- [ ] Knowledge entries listed and searchable
- [ ] Manual entry creation works
- [ ] Delete removes from KB
- [ ] Clicking entry shows source run""",
        ["frontend", "intelligence", "enhancement", "new-feature"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[FE-4] Enhanced settings hub — models, API keys, integrations, MCP servers",
        """## Summary
Enhance `/dashboard/settings` into a full settings hub with tabbed sections for all configuration.

## Sections
1. **Models** — provider cards showing configured models, API key status (set/not set), test connection button
2. **Integrations** — Jira / Linear / Azure DevOps cards with connection test
3. **MCP Servers** — add/remove MCP server URLs, test connection, view available tools
4. **Browser** — headless mode, viewport size, recording options, screenshot quality
5. **Memory & KB** — memory DB path, KB URI, enable/disable self-evolution

## Files to touch
- `frontend/app/dashboard/settings/page.tsx` — full rewrite with tabs
- `frontend/app/dashboard/settings/components/ModelSettings.tsx` (new)
- `frontend/app/dashboard/settings/components/IntegrationSettings.tsx` (new)
- `frontend/app/dashboard/settings/components/MCPSettings.tsx` (new)
- `backend/app/api/v1/settings.py` (new) — GET/POST settings

## Acceptance Criteria
- [ ] All 5 tabs functional
- [ ] API key status shown (set = green, not set = red)
- [ ] Test connection buttons work
- [ ] Settings persist across page reload""",
        ["frontend", "enhancement", "new-feature"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[FE-5] Analytics dashboard — test coverage trends and agent performance",
        """## Summary
New `/dashboard/analytics` page with charts showing test coverage over time, agent execution durations, pass/fail rates, and KB growth.

## Charts
- Line chart: number of test cases generated per day
- Bar chart: average agent execution time by agent type
- Donut chart: test case types (positive/negative/edge/boundary split)
- Area chart: KB entries over time (knowledge growth)
- Heatmap: which apps/URLs have been tested most

## Tech
- recharts (already in many Next.js projects, add if not present)
- shadcn/ui Card + Chart components
- Data from `GET /api/v1/analytics`

## Files to touch
- `frontend/app/dashboard/analytics/page.tsx` (new)
- `frontend/app/dashboard/analytics/components/*.tsx` (chart components)
- `backend/app/api/v1/analytics.py` (new — aggregate run data)
- `frontend/app/layout/Sidebar.tsx` — add Analytics link

## Acceptance Criteria
- [ ] 5 charts render with real data from run history
- [ ] Charts update when new runs complete
- [ ] Empty state when no runs yet""",
        ["frontend", "enhancement", "new-feature"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[FE-6] Interactive element selection — point-and-click from live page (from QA-SDET)",
        """## Summary
Port the interactive element selection feature from QA-SDET into WAIGenie. User enters a URL, the app opens it in a sandboxed browser view, and they can click on elements to inspect them and generate targeted test cases.

## From QA-SDET
QA-SDET had an Element Inspector route + frontend that let users interact with a live Selenium-driven browser. Port this concept using browser-use instead of Selenium.

## Flow
1. User opens `/dashboard/scout` and enters a URL
2. Backend launches browser-use agent in screenshot mode
3. Frontend shows live screenshots (via SSE)
4. User clicks on element in screenshot → backend identifies element details
5. "Generate test for this element" → pre-fills pipeline with element context

## Files to touch
- `frontend/app/dashboard/scout/page.tsx` (new)
- `frontend/app/dashboard/scout/components/LiveBrowser.tsx` (new)
- `backend/app/api/v1/scout.py` (expand from BE-11)
- `backend/app/agents/site_scout_agent.py` (expand)

## Acceptance Criteria
- [ ] Live browser view shows screenshots
- [ ] Click-to-inspect identifies element selectors
- [ ] "Generate test" fills pipeline with element context""",
        ["frontend", "browser", "enhancement", "from-qa-sdet"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[FE-7] Agent Builder UI — create and manage custom agents",
        """## Summary
New `/dashboard/agents` page where users can define custom agents: set name, role, model, tools, instructions, and deploy them as part of the pipeline.

## UI
- Agent cards: each shows name, model, tools, status (active/inactive)
- Create button: form with fields:
  - Name, description
  - Model picker (all supported providers/models)
  - Tool selector (Jira, Linear, web search, knowledge base, etc.)
  - System instructions editor (CodeMirror or textarea)
  - Response format (markdown/structured)
- Preview: test the agent with a sample prompt
- Activate/deactivate toggle

## Backend
- `AgentDefinition` Pydantic model stored in SQLite
- `build_agent_from_definition()` factory function
- `TOOL_REGISTRY` mapping tool names to Agno tool classes

## Files to touch
- `frontend/app/dashboard/agents/page.tsx` (new)
- `frontend/app/dashboard/agents/components/AgentCard.tsx` (new)
- `frontend/app/dashboard/agents/components/AgentForm.tsx` (new)
- `backend/app/services/agent_registry.py` (new)
- `backend/app/api/v1/agents.py` (new)

## Acceptance Criteria
- [ ] Create custom agent via UI
- [ ] Custom agent available in pipeline model picker
- [ ] Activate/deactivate without restart""",
        ["frontend", "backend", "enhancement", "new-feature"]
    ))
    time.sleep(0.5)

    # ── Production ─────────────────────────────────────────────────────────
    print("\n=== Production ===")

    issues.append(create_issue(TOKEN, REPO,
        "[PROD-1] Docker Compose — all services with health checks and volumes",
        """## Summary
Create a production-ready `docker-compose.yml` with all WAIGenie services, health checks, volume mounts for persistence, and optional PgVector/Redis.

## Services
- `backend` — FastAPI (port 8000), health check: `GET /health`
- `frontend` — Next.js (port 3000)
- `db` (optional) — PostgreSQL + pgvector extension
- `redis` (optional) — for task queue / caching

## Files to touch
- `docker-compose.yml` (update existing)
- `docker-compose.prod.yml` (new — production overrides)
- `backend/Dockerfile` (optimize: multi-stage, slim base)
- `frontend/Dockerfile` (optimize: multi-stage)
- `.env.example` (add Docker-specific vars)

## Acceptance Criteria
- [ ] `docker-compose up` starts all services
- [ ] Health checks pass within 30 seconds
- [ ] Data persists across container restarts (volumes)
- [ ] `docker-compose.prod.yml` uses production settings""",
        ["production", "enhancement"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[PROD-2] Rate limiting + async task queue for browser execution jobs",
        """## Summary
Add request rate limiting (slowapi) and a background task queue (asyncio Queue or ARQ) so multiple concurrent browser execution requests are queued and processed in order.

## Why
Browser execution is resource-intensive. Without queuing:
- Multiple simultaneous users crash the server
- Memory/CPU spikes cause OOM kills

## Implementation
```python
# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
@router.post("/execute")
@limiter.limit("5/minute")
async def execute(...): ...

# Task queue
class BrowserJobQueue:
    _queue: asyncio.Queue = asyncio.Queue(maxsize=10)

    async def enqueue(self, job: BrowserJob) -> str:
        job_id = str(uuid4())
        await self._queue.put(job)
        return job_id

    async def worker(self):
        while True:
            job = await self._queue.get()
            await process_browser_job(job)
```

## Files to touch
- `backend/app/services/job_queue.py` (new)
- `backend/app/api/v1/execute.py` — use job queue
- `backend/app/main.py` — start queue worker in lifespan
- `backend/requirements.txt` — add slowapi

## Acceptance Criteria
- [ ] Rate limit: 5 browser executions/minute per IP
- [ ] Queue: max 10 concurrent jobs, others wait
- [ ] Job status polling: `GET /api/v1/jobs/{job_id}`""",
        ["production", "backend", "enhancement"]
    ))
    time.sleep(0.5)

    issues.append(create_issue(TOKEN, REPO,
        "[PROD-3] Groq integration — add Groq models for ultra-fast inference",
        """## Summary
Extend the existing Groq entry in `model_factory.py` with the latest Llama 4 models and add Groq as a selectable option in the frontend model picker.

## Models to Add
- `llama-4-scout-17b-16e-instruct` (vision capable, fast)
- `llama-4-maverick-17b-128e-instruct` (most capable Llama 4)
- `llama-3.3-70b-versatile` (strong reasoning)
- `gemma2-9b-it` (lightweight)

## Why Groq
- 10-50x faster inference than standard APIs
- Great for iterative test generation (fast feedback)
- Cost-effective for high-volume test generation

## Files to touch
- `backend/app/utils/model_factory.py` — add Groq model IDs
- `frontend/app/dashboard/settings/page.tsx` — add Groq section
- `backend/.env.example` — add GROQ_API_KEY note

## Acceptance Criteria
- [ ] Groq models appear in model picker
- [ ] Full pipeline runs with llama-4-scout
- [ ] Vision-capable models work with browser execution""",
        ["backend", "enhancement", "new-feature"]
    ))
    time.sleep(0.5)

    print(f"\n=== Done! Created {len([i for i in issues if i])} issues on {REPO} ===")
    print("\nNext steps:")
    print("1. Add GitHub labels if not already set")
    print("2. Review issues and assign milestones")
    print("3. Start with [BE-1], [BE-2], [BE-3] for the intelligence layer")


if __name__ == "__main__":
    main()
