#!/usr/bin/env python3
"""
WAIGenie Deep Feature Issues — All 5 Phases
Creates detailed, implementation-ready GitHub issues.

Usage:
    python docs/create-deep-issues.py --token YOUR_TOKEN --repo richard-devbot/waigenie-qa
"""
import argparse, json, time, urllib.request, urllib.error

def post(token, repo, path, data):
    url = f"https://api.github.com/repos/{repo}/{path}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
        headers={"Authorization": f"token {token}",
                 "Accept": "application/vnd.github.v3+json",
                 "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"  ERR {e.code}: {e.read().decode()[:120]}")
        return {}

def label(token, repo, name, color, desc=""):
    r = post(token, repo, "labels", {"name": name, "color": color, "description": desc})
    if r.get("name"):  print(f"  label: {name}")
    else:              print(f"  label exists or failed: {name}")

def issue(token, repo, title, body, labels):
    r = post(token, repo, "issues", {"title": title, "body": body, "labels": labels})
    if r.get("number"):
        print(f"  #{r['number']}: {title}")
    time.sleep(0.6)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--token", required=True)
    p.add_argument("--repo", default="richard-devbot/waigenie-qa")
    a = p.parse_args()
    T, R = a.token, a.repo

    # ── Labels ───────────────────────────────────────────────────────────────
    print(f"\n=== Labels → {R} ===")
    for name, color, desc in [
        ("phase-1-intelligence", "0052cc", "Structured outputs, Reasoning, Workflow 2.0, Teams"),
        ("phase-2-browser",      "0e8a16", "Browser profiles, Skills, Judge, Sessions"),
        ("phase-3-analysis",     "e4e669", "Security, A11y, Visual Regression, DOM Proxy"),
        ("phase-4-realtime",     "5319e7", "SSE Streaming, Run History, Analytics"),
        ("phase-5-frontiers",    "b60205", "SiteScout, Skill Library, Agent Builder, Multi-LLM"),
        ("backend",  "1d76db", "Python / FastAPI"),
        ("frontend", "fbca04", "Next.js / TypeScript"),
        ("agno",     "0075ca", "Agno framework feature"),
        ("browser-use", "006b75", "browser-use library feature"),
        ("from-qa-sdet",    "c2e0c6", "Ported from QA-SDET project"),
        ("from-sdet-genie", "bfdadc", "Ported from SDET-GENIE project"),
        ("new-feature", "d4c5f9", "Net-new capability"),
        ("breaking-change", "d93f0b", "May require migration"),
    ]:
        label(T, R, name, color, desc)
        time.sleep(0.25)

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 1 — INTELLIGENCE CORE
    # ════════════════════════════════════════════════════════════════════════
    print("\n\n=== PHASE 1: Intelligence Core ===")

    issue(T, R, "[P1-1] Structured Pydantic outputs for all 5 agents (response_model=)",
"""## Problem
All 5 agents currently return raw markdown strings. The frontend parses them with fragile string splitting. Any prompt change breaks the UI.

## Solution
Use Agno's `response_model=` parameter to return validated Pydantic objects from every agent.

## Pydantic Models to Create
**File:** `backend/app/models/agent_outputs.py`

```python
from pydantic import BaseModel, Field
from typing import Literal

class EnhancedStory(BaseModel):
    title: str
    as_a: str
    i_want: str
    so_that: str
    acceptance_criteria: list[str]
    implementation_notes: list[str]
    testability_notes: list[str]
    related_epics: list[str] = []
    jira_ticket_id: str | None = None

class TestCase(BaseModel):
    id: str                    # TC-001
    title: str
    type: Literal["positive", "negative", "edge", "boundary", "performance", "security"]
    preconditions: list[str]
    steps: list[str]
    expected_result: str
    test_data: dict = {}
    priority: Literal["critical", "high", "medium", "low"]
    automation_status: Literal["automatable", "manual-only", "already-automated"]

class TestCaseList(BaseModel):
    feature: str
    total: int
    test_cases: list[TestCase]

class GherkinScenario(BaseModel):
    title: str
    tags: list[str] = []
    given: list[str]
    when: list[str]
    then: list[str]
    examples: list[dict] = []   # for Scenario Outline
    entry_point_url: str | None = None

class GherkinFeature(BaseModel):
    feature_name: str
    description: str = ""
    background: list[str] = []
    scenarios: list[GherkinScenario]

class GeneratedCode(BaseModel):
    framework: str
    language: str
    imports: list[str]
    page_object_class: str | None = None
    test_class: str
    helper_functions: list[str] = []
    requirements: list[str] = []  # pip packages needed
```

## Agent Changes
Each agent gets `response_model=` and `structured_outputs=True`:
```python
# user_story_agent.py
agent = Agent(
    model=model,
    response_model=EnhancedStory,
    structured_outputs=True,
    ...
)
```

## Service Changes
`StoryService.enhance_user_story()` returns `EnhancedStory` directly instead of raw dict.

## Frontend Impact
- Remove all regex string parsing
- TypeScript interfaces mirror the Pydantic models exactly
- Components receive typed props

## Files
- `backend/app/models/agent_outputs.py` (new)
- `backend/app/agents/*.py` — add `response_model=`
- `backend/app/services/*.py` — update return types
- `frontend/lib/types.ts` — add TypeScript interfaces
- `frontend/app/dashboard/pipeline/components/results/*.tsx` — simplify rendering

## Acceptance Criteria
- [ ] All 5 agents return Pydantic objects
- [ ] No regex parsing anywhere in services
- [ ] Frontend renders structured fields directly
- [ ] Pydantic validation errors return 422 with clear message
- [ ] Backward-compatible: old string format still works via `content` field fallback""",
["phase-1-intelligence", "backend", "agno", "breaking-change"])

    issue(T, R, "[P1-2] ReasoningTools — agents think step-by-step before generating",
"""## Problem
Agents produce test cases and Gherkin in one shot. Complex stories often result in shallow, low-quality tests because the agent doesn't "think" before generating.

## Solution
Add Agno `ReasoningTools` to the TestCraft and GherkinGen agents so they reason through the problem first, then generate output.

## How It Works (Agno)
```python
from agno.tools.reasoning import ReasoningTools

test_agent = Agent(
    model=model,
    tools=[ReasoningTools(add_instructions=True)],
    response_model=TestCaseList,
    instructions=[
        "Before generating test cases, use think() to:",
        "1. Identify the core user journey",
        "2. List all edge cases and boundary conditions",
        "3. Determine security and performance implications",
        "Then generate comprehensive test cases based on your analysis"
    ]
)
```

## Reasoning Chain for TestCraft
The agent should reason through:
- What is the happy path?
- What data inputs could break this?
- What authentication/authorization edge cases exist?
- What happens on network failure?
- What are the performance thresholds?

## Reasoning Chain for GherkinGen
- Is this scenario truly independent?
- What is the minimum Given context needed?
- Does the When step have exactly one action?
- Does the Then step verify observable behavior?

## Expected Quality Improvement
- 30-50% more edge cases identified
- More specific, testable acceptance criteria
- Fewer "happy path only" test suites

## Files
- `backend/app/agents/test_case_agent.py` — add ReasoningTools
- `backend/app/agents/gherkin_agent.py` — add ReasoningTools
- `backend/requirements.txt` — verify `agno>=1.7.0`

## Acceptance Criteria
- [ ] TestCraft agent shows reasoning trace in debug output
- [ ] GherkinGen produces scenarios that follow BDD best practices
- [ ] Quality: each story generates positive + negative + edge cases
- [ ] Reasoning adds < 3s latency on average
- [ ] Reasoning can be disabled via `ENABLE_REASONING=false` env var""",
["phase-1-intelligence", "backend", "agno", "new-feature"])

    issue(T, R, "[P1-3] Agno Workflow 2.0 — parallel TestCraft + GherkinGen pipeline",
"""## Problem
The current pipeline runs all 5 stages sequentially: Story → Tests → Gherkin → Browser → Code. Stages 2 and 3 are independent and could run in parallel, saving 30-60 seconds per run.

## Solution
Replace the manual `asyncio.create_task` chaining in `pipeline_service.py` with an Agno `Workflow` using `Parallel()` for independent steps.

## New Pipeline Architecture
```python
from agno.workflow import Step, Workflow
from agno.workflow.parallel import Parallel

# Steps
story_step    = Step(name="StoryForge",  agent=story_agent)
test_step     = Step(name="TestCraft",   agent=test_agent)
gherkin_step  = Step(name="GherkinGen",  agent=gherkin_agent)
browser_step  = Step(name="BrowserPilot", agent=browser_agent)
code_step     = Step(name="CodeSmith",   agent=code_agent)

qa_workflow = Workflow(
    name="QA Pipeline",
    db=SqliteDb(db_file="./waigenie_sessions.db"),
    steps=[
        story_step,
        Parallel(test_step, gherkin_step, name="Analysis Phase"),
        browser_step,
        code_step,
    ]
)
```

## Session Persistence
Workflow uses `SqliteDb` to persist session state — users can resume interrupted pipelines:
```python
# Resume from where it left off
qa_workflow.run(input=story, session_id="existing-session-id")
```

## Step Input/Output Bridging
```python
def bridge_story_to_parallel(step_input: StepInput) -> StepOutput:
    \"\"\"Feed enhanced story to BOTH TestCraft and GherkinGen.\"\"\"
    return StepOutput(content=step_input.previous_step_content)
```

## Benefits
- 30-60s faster per run (parallel analysis phase)
- Pipeline sessions are resumable
- Clean separation of concerns
- Workflow state visible in UI

## Files
- `backend/app/services/pipeline_service.py` — replace manual chaining with Workflow
- `backend/app/workflows/qa_workflow.py` (new)
- `backend/app/workflows/__init__.py` (new)
- `backend/requirements.txt` — agno workflow deps

## Acceptance Criteria
- [ ] TestCraft and GherkinGen run simultaneously
- [ ] Total pipeline time reduced by 25%+ for 3+ scenario runs
- [ ] Session state persisted — restart server mid-run, pipeline resumes
- [ ] Each step's output correctly feeds the next step
- [ ] Parallel step failures handled gracefully (one fails, other continues)""",
["phase-1-intelligence", "backend", "agno", "new-feature"])

    issue(T, R, "[P1-4] Agno Team coordinate mode — QA Master Orchestrator",
"""## Problem
There is no top-level orchestrator. Failures in one stage cause the whole pipeline to crash. There's no way to retry a stage with a different model, or skip a stage intelligently.

## Solution
Wrap all 5 agents in an Agno `Team` with `TeamMode.coordinate`. The Master QA Orchestrator decides which specialist to call, handles failures, and can try a different model on retry.

## Architecture
```python
from agno.team import Team
from agno.team.mode import TeamMode

qa_team = Team(
    name="QA Master Orchestrator",
    mode=TeamMode.coordinate,
    model=orchestrator_model,   # Use best available model for orchestration
    members=[
        story_agent,    # StoryForge
        test_agent,     # TestCraft
        gherkin_agent,  # GherkinGen
        browser_agent,  # BrowserPilot
        code_agent,     # CodeSmith
    ],
    output_schema=PipelineResult,  # Typed final output
    instructions=[
        "You are the QA Master Orchestrator.",
        "Run StoryForge first, then TestCraft and GherkinGen in parallel.",
        "If BrowserPilot fails, skip it and generate code from Gherkin alone.",
        "Always produce a complete PipelineResult even with partial data.",
    ],
    show_members_responses=True,
    enable_agentic_context=True,
)
```

## Intelligent Failure Handling
- BrowserPilot fails → CodeSmith uses Gherkin only (no element data)
- GherkinGen fails → BrowserPilot uses TestCases directly
- API rate limit → switch member to Groq (fast, cheap fallback)

## Files
- `backend/app/agents/orchestrator.py` (new)
- `backend/app/services/pipeline_service.py` — use Team instead of manual service calls
- `backend/app/models/agent_outputs.py` — add `PipelineResult` model

## Acceptance Criteria
- [ ] Team orchestrates full 5-step pipeline
- [ ] Browser failure → CodeSmith still generates code from Gherkin
- [ ] Team response includes which members were called and in what order
- [ ] `show_members_responses=True` feeds into SSE streaming
- [ ] Orchestrator model configurable separately from member models""",
["phase-1-intelligence", "backend", "agno", "new-feature"])

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 2 — BETTER BROWSER
    # ════════════════════════════════════════════════════════════════════════
    print("\n=== PHASE 2: Better Browser ===")

    issue(T, R, "[P2-1] Browser profiles — persistent login sessions across test runs",
"""## Problem
Every pipeline run starts a fresh browser with no login state. Users testing authenticated apps must add "login" steps to every single Gherkin scenario, wasting browser steps and making scenarios fragile.

## Solution
Implement browser-use's Profile system. One profile per user/app combination. Login once, reuse the session for all subsequent test runs.

## How It Works (browser-use)
```python
from browser_use import BrowserProfile, BrowserSession

# Create profile once (user does this in Settings UI)
profile = BrowserProfile(
    name="my-app-profile",
    cookies_file="./profiles/my-app.json",   # persisted login state
    storage_state="./profiles/my-app-state.json"
)

# Each test run reuses the profile
session = BrowserSession(browser_profile=profile)
agent = Agent(browser_session=session, ...)
```

## Profile Management API
```
POST   /api/v1/profiles                # Create profile
GET    /api/v1/profiles                # List profiles
DELETE /api/v1/profiles/{id}           # Delete
POST   /api/v1/profiles/{id}/capture   # Open browser, user logs in manually, save state
GET    /api/v1/profiles/{id}/status    # Check if cookies are still valid
```

## Profile Capture Flow (UI)
1. User clicks "Create Profile" → name the profile + enter app URL
2. Backend opens browser in non-headless mode
3. User logs in manually
4. User clicks "Save Profile" → cookies/storage captured
5. All future runs for that app use this profile

## Storage
- Profile metadata in SQLite (`profiles` table)
- Cookie/state files at `./profiles/{profile_id}/`
- Profile linked to specific domain

## Gherkin Impact
Scenarios no longer need login steps:
```gherkin
# Before (fragile):
Given I am on "https://app.com/login"
When I type "user@email.com" in the email field
And I type "password123" in the password field
And I click the Login button

# After (with profile):
Given I am logged into "my-app-profile"
When I navigate to "https://app.com/dashboard"
```

## Files
- `backend/app/browser/profile_manager.py` (new)
- `backend/app/api/v1/profiles.py` (new)
- `backend/app/models/request_models.py` — add ProfileCreate, ProfileResponse
- `frontend/app/dashboard/settings/page.tsx` — Profile Management section

## Acceptance Criteria
- [ ] User can create a named profile by logging in manually
- [ ] Profile cookies/state persisted to disk
- [ ] Pipeline runs with selected profile skip login steps
- [ ] Profile validity check (re-capture if expired)
- [ ] Profiles listed and manageable in Settings UI""",
["phase-2-browser", "backend", "frontend", "browser-use", "new-feature"])

    issue(T, R, "[P2-2] browser-use Skill system — reusable named browser tasks",
"""## Problem
Common browser sequences (login, checkout, form submission, search) are re-discovered in every run. There is no way to say "use the login skill I already verified works for this app".

## Solution
Implement a Skill Library backed by browser-use's skill system. Skills are named, reusable browser task sequences stored with their verified steps.

## Skill Definition
```python
class BrowserSkill(BaseModel):
    id: str                    # UUID
    name: str                  # "Login to Salesforce CRM"
    description: str
    domain: str                # "salesforce.com"
    task_prompt: str           # The exact task string for browser-use
    verified_steps: list[str]  # XPaths/selectors that worked
    success_rate: float        # 0.0 - 1.0
    use_count: int
    last_used: datetime | None
    profile_id: str | None     # Associated browser profile
    tags: list[str]

# Usage in BrowserPilot
skill = skill_library.get("login-to-salesforce")
if skill:
    task = f"Use this verified approach: {skill.task_prompt}\\n\\nKnown selectors: {skill.verified_steps}"
else:
    task = gherkin_scenario  # Fall back to raw Gherkin
```

## Auto-Promotion
After a skill is used successfully 3 times → auto-promote to "verified":
```python
async def record_skill_use(skill_id: str, success: bool):
    skill = await db.get_skill(skill_id)
    skill.use_count += 1
    if success:
        skill.success_rate = (skill.success_rate * (skill.use_count-1) + 1) / skill.use_count
    if skill.use_count >= 3 and skill.success_rate > 0.8:
        skill.status = "verified"
    await db.save_skill(skill)
```

## Skill Discovery (from SiteScout — P5-1)
SiteScout auto-generates skills from URL exploration. Manual creation also available.

## API
```
GET    /api/v1/skills                 # List skills (filterable by domain/tag)
POST   /api/v1/skills                 # Create skill manually
PUT    /api/v1/skills/{id}            # Update
DELETE /api/v1/skills/{id}
POST   /api/v1/skills/{id}/test       # Test skill in live browser
GET    /api/v1/skills/suggest?url=    # Suggest skills for a given URL
```

## Files
- `backend/app/intelligence/skill_library.py` (new)
- `backend/app/api/v1/skills.py` (new)
- `backend/app/db/models.py` — add BrowserSkill table
- `frontend/app/dashboard/knowledge/page.tsx` — Skill Library tab

## Acceptance Criteria
- [ ] Skills stored with verified selectors
- [ ] BrowserPilot checks skill library before executing Gherkin
- [ ] Auto-promotion after 3 successful uses
- [ ] Skills browsable/searchable in UI
- [ ] Skill test button runs skill in live browser""",
["phase-2-browser", "backend", "frontend", "browser-use", "new-feature"])

    issue(T, R, "[P2-3] Judge mode — self-verification after each browser execution",
"""## Problem
BrowserPilot can "complete" a scenario while actually failing (wrong page, missing element, silently wrong). There's no self-verification step.

## Solution
After each browser execution, run a separate "Judge" agent that reviews screenshots + extracted content and verdicts pass/fail/partial with evidence.

## How It Works (browser-use Judge)
```python
from browser_use import Agent

judge_agent = Agent(
    task=f\"\"\"
    Review the browser execution results for this Gherkin scenario:
    {scenario}

    Screenshots taken: {screenshot_paths}
    Final page URL: {final_url}
    Elements found: {element_summary}

    Verdict:
    - PASS: All Then steps verified with visual/DOM evidence
    - PARTIAL: Some steps completed, some inconclusive
    - FAIL: One or more Then steps clearly not achieved

    Provide specific evidence for your verdict.
    \"\"\",
    llm=vision_llm,   # Must be vision-capable model
)

class ExecutionVerdict(BaseModel):
    scenario_title: str
    verdict: Literal["PASS", "PARTIAL", "FAIL"]
    evidence: list[str]         # Screenshots/DOM evidence
    failed_steps: list[str]     # Which Then steps failed
    confidence: float           # 0.0 - 1.0
    suggestions: list[str]      # How to fix if failed
```

## Integration with Self-Evolution
- PASS → extract selectors → save to KB with high confidence
- PARTIAL → save selectors with medium confidence
- FAIL → mark selectors as unreliable in KB

## UI Presentation
Each scenario card shows verdict badge:
- ✅ PASS (green)
- ⚠️ PARTIAL (yellow) + which steps
- ❌ FAIL (red) + evidence + suggestions

## Files
- `backend/app/agents/judge_agent.py` (new)
- `backend/app/services/browser_execution_service.py` — call judge after execution
- `backend/app/models/agent_outputs.py` — add ExecutionVerdict
- `frontend/app/dashboard/pipeline/components/results/` — verdict display

## Acceptance Criteria
- [ ] Judge runs after every scenario execution
- [ ] Verdict shown per scenario in UI
- [ ] FAIL verdict includes specific evidence (screenshot reference)
- [ ] Self-evolution uses verdict to calibrate KB confidence
- [ ] Judge can be disabled via settings (for speed-first mode)""",
["phase-2-browser", "backend", "agno", "browser-use", "new-feature"])

    issue(T, R, "[P2-4] Session keep-alive — carry browser state across Gherkin scenarios",
"""## Problem
Each Gherkin scenario runs in a completely fresh browser session. For multi-step user journeys (login → add to cart → checkout), the test must re-login for every scenario. This is slow and unrealistic.

## Solution
Add a `session_strategy` option: `isolated` (current default) or `continuous` (shared session across all scenarios in a feature).

## Architecture
```python
class SessionStrategy(str, Enum):
    ISOLATED   = "isolated"   # Fresh browser per scenario (default)
    CONTINUOUS = "continuous" # One browser, scenarios run in sequence

# In BrowserExecutionService:
async def execute_feature(
    scenarios: list[GherkinScenario],
    strategy: SessionStrategy = SessionStrategy.ISOLATED,
    profile_id: str | None = None,
):
    if strategy == SessionStrategy.CONTINUOUS:
        # One session, sequential
        session = await BrowserSession.create(profile=profile_id)
        results = []
        for scenario in scenarios:
            result = await run_scenario_in_session(scenario, session)
            results.append(result)
            # Carry context: visited_urls, current_url, session_data
        await session.close()
        return results
    else:
        # Parallel isolated (current behavior)
        return await asyncio.gather(*[
            run_isolated(s) for s in scenarios
        ])
```

## Gherkin Feature-Level Strategy
Specify strategy in the Feature header:
```gherkin
@continuous-session
Feature: E-commerce Purchase Flow
  Background:
    Given I am logged in as "test@example.com"  # runs ONCE, shared

  Scenario: Add item to cart
    When I search for "laptop"
    And I click the first result
    And I add it to cart

  Scenario: Complete checkout        # browser STILL logged in
    When I go to cart
    And I click Checkout
```

## Files
- `backend/app/browser/browser_manager.py` — add session strategy
- `backend/app/services/browser_execution_service.py` — strategy parameter
- `backend/app/models/request_models.py` — add session_strategy field
- `frontend/app/dashboard/pipeline/components/input/PipelineInput.tsx` — strategy selector

## Acceptance Criteria
- [ ] `continuous` mode runs all scenarios in one browser session
- [ ] Login from scenario 1 persists to scenario 2
- [ ] Feature-level `@continuous-session` tag detected and honored
- [ ] `isolated` mode unchanged (parallel execution preserved)
- [ ] Session context (URLs, cookies) exported to run artifacts""",
["phase-2-browser", "backend", "frontend", "browser-use", "new-feature"])

    issue(T, R, "[P2-5] Two-phase Gherkin — Manual-first approach from QA-SDET",
"""## Problem
The current GherkinGen agent generates scenarios directly from user stories in one step. This produces scenarios that are too high-level and miss implementation details.

## Solution
Port QA-SDET's two-phase Gherkin generation:
1. **Phase 1**: User Story → Detailed Manual Test Cases (TestCraft)
2. **Phase 2**: Manual Test Cases → Gherkin Scenarios (GherkinGen)

The manual test cases act as a "thinking scaffold" that improves Gherkin quality.

## QA-SDET Approach (to port)
From `gherkin_generator.py`:
```python
# Method: "manual-first"
def generate_gherkin_manual_first(story: str) -> GherkinFeature:
    # Phase 1: Generate rich manual test cases first
    manual_cases = llm.generate_manual_test_cases(story)

    # Phase 2: Convert each manual case to a scenario
    # Manual test case structure guides the Gherkin:
    # - Preconditions → Given steps
    # - Test steps    → When steps
    # - Expected result → Then steps
    feature = llm.convert_manual_to_gherkin(story, manual_cases)
    return feature
```

## Detail Level Control (also from QA-SDET)
```python
class GherkinDetail(str, Enum):
    SIMPLE   = "simple"    # 3-5 scenarios, basic steps
    DETAILED = "detailed"  # Outlines, examples, backgrounds, tags
    EXHAUSTIVE = "exhaustive"  # All edge cases, performance, security tags
```

## Scenario Outline Generation
For data-driven tests, automatically generate `Scenario Outline` with `Examples`:
```gherkin
Scenario Outline: Login with various credentials
  Given I am on "<url>/login"
  When I enter "<email>" and "<password>"
  Then I should see "<expected_result>"

  Examples:
    | email              | password    | expected_result        |
    | valid@example.com  | correct123  | Dashboard              |
    | valid@example.com  | wrong       | Invalid credentials    |
    | invalid@           | any         | Invalid email format   |
```

## Files
- `backend/app/agents/gherkin_agent.py` — add `generation_mode` and `detail_level` params
- `backend/app/services/gherkin_service.py` — two-phase flow
- `backend/app/models/request_models.py` — add `gherkin_mode` and `detail_level`
- `frontend/app/dashboard/pipeline/components/input/PipelineInput.tsx` — mode selector

## Acceptance Criteria
- [ ] `manual-first` mode produces noticeably better Gherkin
- [ ] `detail=detailed` produces Scenario Outlines with Examples tables
- [ ] `detail=simple` produces 3-5 basic scenarios (fast mode)
- [ ] Manual test cases shown as intermediate step in UI
- [ ] Both modes produce valid, parseable Gherkin syntax""",
["phase-2-browser", "backend", "from-qa-sdet", "new-feature"])

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 3 — ANALYSIS SUITE
    # ════════════════════════════════════════════════════════════════════════
    print("\n=== PHASE 3: Analysis Suite ===")

    issue(T, R, "[P3-1] Element analysis suite — Security, A11y, Visual Regression, Performance",
"""## Problem
WAIGenie generates test cases but doesn't analyze the quality or safety of the elements being tested. QA-SDET has a sophisticated element analysis suite that WAIGenie lacks.

## Solution
Port and enhance QA-SDET's `llm_services.py` analysis functions into a dedicated `AnalysisService`.

## Analysis Types (from QA-SDET)

### 1. Security Analysis
```python
async def analyze_element_security(element: ElementDetails) -> SecurityReport:
    \"\"\"Detect: XSS vectors, SQL injection via form fields, CSRF risk,
    open redirect, sensitive data exposure, missing CSP headers.\"\"\"
    # Uses vision-capable LLM to inspect element + surrounding HTML
```

### 2. Accessibility Audit (WCAG 2.1)
```python
async def analyze_accessibility(element: ElementDetails) -> A11yReport:
    \"\"\"Check: alt text, aria-label, role attributes, color contrast,
    focus management, keyboard navigation, screen reader compatibility.\"\"\"
```

### 3. Visual Regression
```python
async def detect_visual_regression(
    baseline_screenshot: str,  # path from previous run
    current_screenshot: str,
) -> VisualRegressionReport:
    \"\"\"Compare screenshots pixel-by-pixel + AI analysis.
    Detect: layout shifts, color changes, missing elements, text changes.\"\"\"
```

### 4. Performance Insights
```python
async def generate_performance_insights(har_file: str) -> PerformanceReport:
    \"\"\"From HAR file: slow requests (>500ms), large payloads (>1MB),
    blocking resources, caching opportunities, API error rates.\"\"\"
```

## New API Endpoints
```
POST /api/v1/analyze/security      — element security scan
POST /api/v1/analyze/accessibility — WCAG audit
POST /api/v1/analyze/visual        — compare two screenshots
POST /api/v1/analyze/performance   — HAR file analysis
POST /api/v1/analyze/full          — all four in parallel
```

## Pydantic Output Models
```python
class SecurityFinding(BaseModel):
    severity: Literal["critical", "high", "medium", "low", "info"]
    type: str        # "XSS", "SQLi", "CSRF", etc.
    element: str     # selector
    evidence: str
    recommendation: str

class A11yViolation(BaseModel):
    wcag_criterion: str   # "1.1.1", "2.4.7", etc.
    level: Literal["A", "AA", "AAA"]
    element: str
    issue: str
    fix: str
```

## UI Integration
After browser execution completes, show 4 analysis tabs in results:
- 🔐 Security (N findings)
- ♿ Accessibility (N violations)
- 👁️ Visual (N changes from baseline)
- ⚡ Performance (N issues from HAR)

## Files
- `backend/app/services/analysis_service.py` (new)
- `backend/app/agents/analysis_agent.py` (new)
- `backend/app/api/v1/analyze.py` (new)
- `backend/app/models/agent_outputs.py` — add report models
- `frontend/app/dashboard/pipeline/components/results/AnalysisPanel.tsx` (new)

## Acceptance Criteria
- [ ] Security scan detects common XSS vectors in input fields
- [ ] A11y audit flags missing aria-labels and alt text
- [ ] Visual regression detects 10%+ layout changes
- [ ] Performance report identifies requests > 500ms from HAR
- [ ] Full analysis runs in parallel (all 4 simultaneously)""",
["phase-3-analysis", "backend", "frontend", "from-qa-sdet", "new-feature"])

    issue(T, R, "[P3-2] Interactive element selection — click any element on a live page",
"""## Problem
Users can only test what they describe in words. They can't point at a specific element on their live app and say "generate a test for THIS button".

## Solution
Port QA-SDET's Element Inspector into WAIGenie's modern FastAPI + Next.js stack. User opens a live page, clicks on any element, gets its selectors and can immediately generate a targeted test.

## QA-SDET Source
`app/routes/element_inspector.py` — DOM proxy + JavaScript XPath injection

## How It Works
1. User enters URL in Element Inspector panel
2. Backend fetches the page via proxy (spoofs headers to avoid bot detection)
3. Injects JavaScript for XPath/CSS extraction + click tracking
4. Proxied page renders in iframe in frontend
5. User clicks element → JS fires `postMessage` with element details
6. Frontend shows element details + selector options
7. "Generate test for this element" → pre-fills pipeline

## JavaScript Injection (from QA-SDET)
```javascript
// Injected into proxied page
document.addEventListener('click', (e) => {
    e.preventDefault();
    const el = e.target;
    const details = {
        tag: el.tagName,
        id: el.id,
        classes: el.className,
        text: el.innerText?.slice(0, 100),
        xpath: getXPath(el),      // relative + absolute
        css: getCSSSelector(el),
        ariaLabel: el.getAttribute('aria-label'),
        dataTestid: el.getAttribute('data-testid'),
        placeholder: el.placeholder,
        type: el.type,
        rect: el.getBoundingClientRect()
    };
    window.parent.postMessage({type: 'element-selected', data: details}, '*');
});
```

## Backend Proxy API
```
POST /api/v1/inspect/load    — fetch + inject + return proxied HTML
POST /api/v1/inspect/analyze — analyze a specific element (security, a11y)
POST /api/v1/inspect/generate-test — generate Gherkin from element details
```

## Files
- `backend/app/services/inspector_service.py` (new)
- `backend/app/api/v1/inspect.py` (new)
- `frontend/app/dashboard/inspect/page.tsx` (new)
- `frontend/app/dashboard/inspect/components/ProxyFrame.tsx` (new)
- `frontend/app/dashboard/inspect/components/ElementPanel.tsx` (new)

## Acceptance Criteria
- [ ] Load any public URL in the inspector iframe
- [ ] Click any element → get full selector details
- [ ] "Generate test" creates a pre-filled pipeline form
- [ ] Element analysis (security + a11y) runs on selected element
- [ ] Proxy handles CORS and header spoofing transparently""",
["phase-3-analysis", "backend", "frontend", "from-qa-sdet", "new-feature"])

    issue(T, R, "[P3-3] DOM proxy with accurate JavaScript XPath generation",
"""## Problem
WAIGenie's element tracker generates XPath server-side from DOM tree data. QA-SDET generates XPath client-side using JavaScript, which produces more accurate relative paths that are resilient to DOM structure changes.

## Solution
Implement client-side XPath + CSS generation via JavaScript injection, used both in the Element Inspector and during live browser execution.

## JavaScript XPath Algorithm (from QA-SDET's element_inspector.py)
```javascript
function getXPath(el) {
    // Prefer: attribute-based (id, data-testid, aria-label)
    if (el.id) return `//${el.tagName.toLowerCase()}[@id='${el.id}']`;
    if (el.dataset.testid) return `//*[@data-testid='${el.dataset.testid}']`;
    if (el.getAttribute('aria-label')) return `//*[@aria-label='${el.getAttribute("aria-label")}']`;

    // Fallback: positional relative path
    const parts = [];
    while (el && el.nodeType === Node.ELEMENT_NODE) {
        let idx = 1;
        let sib = el.previousSibling;
        while (sib) { if (sib.nodeType === 1 && sib.tagName === el.tagName) idx++; sib = sib.previousSibling; }
        parts.unshift(`${el.tagName.toLowerCase()}[${idx}]`);
        el = el.parentNode;
    }
    return '/' + parts.join('/');
}

function getCSSSelector(el) {
    // Priority: data-testid > id > name > aria-label > class chain
    if (el.dataset.testid) return `[data-testid="${el.dataset.testid}"]`;
    if (el.id) return `#${el.id}`;
    if (el.name) return `${el.tagName.toLowerCase()}[name="${el.name}"]`;
    // ... class chain fallback
}
```

## Integration Points
1. **Element Inspector** (P3-2) — inject on page load
2. **BrowserPilot** — inject after navigation to capture real DOM XPaths
3. **Self-evolution** — compare JS-generated vs browser-use-generated selectors

## Quality Improvement
JS-generated XPath outperforms server-side in 3 key areas:
- Relative paths don't break on parent structure changes
- Attribute-first strategy matches QA best practices
- Captures dynamic `data-*` attributes browser-use misses

## Files
- `backend/app/browser/js_injector.py` (new)
- `backend/app/utils/element_tracker.py` — add JS-generated selectors
- `backend/app/services/inspector_service.py` — use in proxy

## Acceptance Criteria
- [ ] JS XPath generation produces attribute-first selectors
- [ ] Relative XPaths generated for all elements
- [ ] JS selectors compared with browser-use selectors (quality score)
- [ ] Better selectors flagged as "recommended" in code output""",
["phase-3-analysis", "backend", "from-qa-sdet"])

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 4 — REAL-TIME & HISTORY
    # ════════════════════════════════════════════════════════════════════════
    print("\n=== PHASE 4: Real-time & History ===")

    issue(T, R, "[P4-1] SSE streaming — real-time pipeline events from every agent",
"""## Problem
The pipeline is a black box while running. Users see a spinner for 2-5 minutes then results appear. There's no visibility into what's happening, and browser screenshots only appear at the end.

## Solution
Add Server-Sent Events streaming so the frontend receives live events as the pipeline progresses.

## Event Schema
```python
class PipelineEvent(BaseModel):
    run_id: str
    timestamp: datetime
    type: Literal[
        "agent_start",       # agent activated
        "agent_thinking",    # ReasoningTools chain step
        "agent_complete",    # agent finished, includes output preview
        "tool_call",         # Jira fetch, KB search, etc.
        "browser_navigate",  # URL navigated to
        "browser_action",    # click/type action
        "browser_screenshot",# new screenshot available
        "browser_step_done", # one Gherkin step complete
        "kb_updated",        # knowledge base updated
        "evolution_complete",# self-evolution finished
        "error",             # non-fatal error
        "complete",          # pipeline done
    ]
    agent: str | None = None       # "StoryForge", "BrowserPilot", etc.
    data: dict = {}
    preview: str | None = None     # short human-readable summary
```

## Backend Implementation
```python
# backend/app/api/v1/stream.py
from fastapi.responses import StreamingResponse
from app.utils.event_bus import EventBus

@router.get("/stream/{run_id}")
async def stream_pipeline(run_id: str):
    bus = EventBus.get(run_id)

    async def generator():
        async for event in bus.listen():
            yield f"data: {event.model_dump_json()}\\n\\n"
            if event.type == "complete": break

    return StreamingResponse(generator(), media_type="text/event-stream",
                              headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

## EventBus (asyncio.Queue per run)
```python
class EventBus:
    _buses: dict[str, asyncio.Queue] = {}

    @classmethod
    def get(cls, run_id: str) -> "EventBus": ...

    async def emit(self, event: PipelineEvent): ...
    async def listen(self): ...
```

## Agent Integration
Each agent emits events via EventBus:
```python
# In each agent's service method:
await event_bus.emit(PipelineEvent(run_id=run_id, type="agent_start", agent="StoryForge"))
result = await story_agent.arun(prompt)
await event_bus.emit(PipelineEvent(run_id=run_id, type="agent_complete", agent="StoryForge",
                                   preview=result.content[:100]))
```

## Files
- `backend/app/api/v1/stream.py` (new)
- `backend/app/utils/event_bus.py` (new)
- `backend/app/services/*.py` — emit events
- `frontend/app/hooks/useSSEPipeline.ts` (new)
- `frontend/app/dashboard/pipeline/components/visualizer/LiveFeed.tsx` (new)

## Acceptance Criteria
- [ ] EventSource connects within 100ms of run start
- [ ] Agent activations visible in real-time
- [ ] Browser screenshots stream live (every 3 seconds during browser step)
- [ ] ReasoningTools chain steps visible as `agent_thinking` events
- [ ] SSE connection auto-reconnects on disconnect
- [ ] Events stored with run for historical replay""",
["phase-4-realtime", "backend", "frontend", "new-feature"])

    issue(T, R, "[P4-2] Run history — persist, browse, and replay all pipeline runs",
"""## Problem
Every pipeline run is ephemeral — results disappear on page refresh or tab close. Users can't compare runs, track progress over time, or reproduce a past run.

## Solution
Persist every pipeline run to SQLite (default) with full results and artifacts.

## Database Schema
```python
class PipelineRun(Base):
    __tablename__ = "pipeline_runs"
    id               = Column(String, primary_key=True)  # UUID
    created_at       = Column(DateTime)
    completed_at     = Column(DateTime, nullable=True)
    user_story_input = Column(Text)
    app_url          = Column(String, nullable=True)
    model_provider   = Column(String)
    model_name       = Column(String)
    framework        = Column(String)
    session_strategy = Column(String)
    profile_id       = Column(String, nullable=True)
    status           = Column(String)   # running/completed/failed/partial
    duration_seconds = Column(Float, nullable=True)
    error_message    = Column(Text, nullable=True)

    # Structured results (JSON columns)
    enhanced_story   = Column(JSON, nullable=True)  # EnhancedStory dict
    test_cases       = Column(JSON, nullable=True)  # list[TestCase]
    gherkin_feature  = Column(JSON, nullable=True)  # GherkinFeature dict
    generated_code   = Column(JSON, nullable=True)  # GeneratedCode dict
    analysis_results = Column(JSON, nullable=True)  # SecurityReport etc.
    evolution_summary= Column(JSON, nullable=True)  # what was learned

    # Artifact paths
    video_path       = Column(String, nullable=True)
    gif_path         = Column(String, nullable=True)
    har_path         = Column(String, nullable=True)
    screenshots      = Column(JSON, nullable=True)   # list of paths
```

## API
```
GET  /api/v1/runs?page=1&limit=20&status=completed  # paginated list
GET  /api/v1/runs/{run_id}                           # full run detail
GET  /api/v1/runs/{run_id}/artifacts/{filename}      # download artifact
POST /api/v1/runs/{run_id}/replay                    # re-run with same settings
DELETE /api/v1/runs/{run_id}                         # delete run + artifacts
GET  /api/v1/runs/compare?ids=id1,id2                # compare two runs
```

## Frontend: Run History Page `/dashboard/history`
- Table with columns: Date | Story Preview | URL | Model | Status | Duration | Actions
- Status badges: ✅ completed / ⏳ running / ❌ failed / ⚠️ partial
- Click row → expandable detail (same result view as pipeline page)
- Download artifacts button (video, HAR, GIF, code files)
- Replay button → pre-fills pipeline form
- Compare button → side-by-side diff of two runs

## Files
- `backend/app/db/models.py` (new — SQLAlchemy models)
- `backend/app/db/session.py` (new — async session factory)
- `backend/app/api/v1/runs.py` (new)
- `backend/app/services/pipeline_service.py` — save run on start/complete
- `frontend/app/dashboard/history/page.tsx` (new)
- `frontend/app/dashboard/history/components/RunTable.tsx` (new)
- `frontend/app/dashboard/history/components/RunDetail.tsx` (new)

## Acceptance Criteria
- [ ] Every pipeline run persisted (start + complete + failure)
- [ ] History page shows last 100 runs with pagination
- [ ] Artifact download works for video/HAR/GIF
- [ ] Replay pre-fills exact same settings
- [ ] Runs survive server restart""",
["phase-4-realtime", "backend", "frontend", "new-feature"])

    issue(T, R, "[P4-3] Analytics dashboard — coverage trends, agent performance, KB growth",
"""## Problem
There's no way to see: how many tests have been generated, which agents are slowest, what apps have been tested most, or how the Knowledge Base is growing over time.

## Solution
Build an analytics dashboard backed by aggregated run history data.

## Metrics to Track
```python
class AnalyticsData(BaseModel):
    # Volume
    total_runs: int
    runs_this_week: int
    runs_trend: list[DayCount]      # last 30 days

    # Quality
    avg_test_cases_per_run: float
    test_type_distribution: dict    # positive/negative/edge split
    pass_rate: float                # judge verdicts

    # Performance
    avg_pipeline_duration: float
    agent_durations: dict[str, float]  # per-agent average seconds
    slowest_runs: list[RunSummary]

    # Knowledge Growth
    kb_entry_count: int
    kb_growth_trend: list[DayCount]
    skill_library_count: int
    most_used_skills: list[SkillUsage]

    # Coverage
    unique_apps_tested: int
    top_apps: list[AppStats]        # most-tested URLs
    framework_distribution: dict    # Playwright vs Selenium etc.
```

## Charts (recharts + shadcn)
1. **Line chart** — runs per day (last 30 days)
2. **Bar chart** — average agent execution time by agent name
3. **Donut chart** — test case type distribution (positive/negative/edge)
4. **Area chart** — KB entries over time
5. **Table** — top 10 most-tested apps with coverage scores
6. **Gauge** — overall pass rate from judge verdicts

## API
```
GET /api/v1/analytics?period=30d   # full analytics payload
GET /api/v1/analytics/agents       # per-agent performance stats
GET /api/v1/analytics/apps         # per-app test coverage
```

## Files
- `backend/app/api/v1/analytics.py` (new)
- `backend/app/services/analytics_service.py` (new — aggregates run history)
- `frontend/app/dashboard/analytics/page.tsx` (new)
- `frontend/app/dashboard/analytics/components/` (chart components)

## Acceptance Criteria
- [ ] All 6 charts render with real data from run history
- [ ] Analytics refresh automatically when new runs complete
- [ ] Date range selector (7d / 30d / 90d / all)
- [ ] Charts export to PNG
- [ ] Empty state with onboarding message if no runs yet""",
["phase-4-realtime", "frontend", "backend", "new-feature"])

    # ════════════════════════════════════════════════════════════════════════
    # PHASE 5 — NEW FRONTIERS
    # ════════════════════════════════════════════════════════════════════════
    print("\n=== PHASE 5: New Frontiers ===")

    issue(T, R, "[P5-1] SiteScout Agent — crawl any URL, auto-generate skill library",
"""## Problem
Before a user can test an app, they have to manually describe it in a user story. For complex apps, this creates a lot of up-front work. There's no way to "bootstrap" an app's test coverage automatically.

## Solution
SiteScout Agent: give it a URL → it crawls the entire app using browser-use → identifies all UI components, interaction patterns, and user journeys → generates and stores Skills in the library.

## Architecture
```python
class SiteScoutAgent:
    async def scout(self, url: str, depth: int = 3) -> ScoutReport:
        # Phase 1: Discover all pages/views
        pages = await self._discover_pages(url, depth)

        # Phase 2: For each page, identify interactive elements
        for page in pages:
            elements = await self._analyze_page_interactions(page)
            skills   = await self._generate_skills_from_elements(elements, page)
            kb.bulk_add_skills(skills)

        # Phase 3: Identify user journeys (multi-page flows)
        journeys = await self._identify_user_journeys(pages)
        for journey in journeys:
            skill_sequence = journey.to_skill_sequence()
            skill_library.save(skill_sequence)

        return ScoutReport(
            pages_discovered=len(pages),
            skills_generated=total_skills,
            journeys_found=len(journeys),
            recommended_test_strategy=self._suggest_strategy(journeys),
        )
```

## Skill Types Generated
- **Login skills** — detected from login form patterns
- **Navigation skills** — menu/nav interactions
- **Form skills** — for each form found
- **Search skills** — search bars and filters
- **CRUD skills** — create/read/update/delete patterns
- **Checkout skills** — e-commerce checkout flows

## Scout Report UI
After scouting, user sees:
- Map of discovered pages (tree view)
- List of generated skills (with preview)
- Suggested test strategy ("This looks like an e-commerce app with 3 main user journeys")
- "Generate full test suite" button (creates stories for all journeys)

## Files
- `backend/app/agents/site_scout_agent.py` (new)
- `backend/app/services/scout_service.py` (new)
- `backend/app/api/v1/scout.py` (new)
- `frontend/app/dashboard/scout/page.tsx` (new)
- `frontend/app/dashboard/scout/components/SiteMap.tsx` (new)

## Acceptance Criteria
- [ ] Given a URL, discovers 5+ pages within depth=2
- [ ] Generates at least 3 reusable skills per page
- [ ] Identifies login flow and creates login skill automatically
- [ ] Scout report shows visual site map
- [ ] "Generate test suite" creates pipeline runs for each journey""",
["phase-5-frontiers", "backend", "frontend", "browser-use", "new-feature"])

    issue(T, R, "[P5-2] Multi-LLM per agent — different model for each pipeline step",
"""## Problem
Currently all agents use the same model/provider. But different tasks benefit from different models: Groq for fast Gherkin generation, GPT-4o for complex story analysis, Gemini for vision-intensive browser execution.

## Solution
Allow each agent to be configured with its own model provider and name. The orchestrator respects per-agent model settings.

## Configuration Schema
```python
class AgentModelConfig(BaseModel):
    story_agent:   ModelRef = ModelRef(provider="Google",    model="gemini-2.5-flash")
    test_agent:    ModelRef = ModelRef(provider="Groq",      model="llama-4-maverick")
    gherkin_agent: ModelRef = ModelRef(provider="Groq",      model="llama-4-scout")
    browser_agent: ModelRef = ModelRef(provider="Google",    model="gemini-2.5-pro")   # vision
    code_agent:    ModelRef = ModelRef(provider="Anthropic", model="claude-sonnet-4-5")

class ModelRef(BaseModel):
    provider: str
    model: str
```

## Smart Defaults (auto-suggest based on capability)
```python
RECOMMENDED_CONFIG = {
    "story_agent":   {"reason": "Needs deep reasoning", "model": "gemini-2.5-pro"},
    "test_agent":    {"reason": "Needs reasoning+speed", "model": "llama-4-maverick"},
    "gherkin_agent": {"reason": "Fast generation fine",  "model": "llama-4-scout"},
    "browser_agent": {"reason": "Vision required",       "model": "gemini-2.5-flash"},
    "code_agent":    {"reason": "Code quality matters",  "model": "claude-sonnet-4-5"},
}
```

## Cost Estimation
Show estimated cost per run based on model selection:
```python
cost = sum([
    token_estimate[agent] * price_per_token[model]
    for agent, model in config.items()
])
# Display: "Estimated cost: $0.003 per run"
```

## UI: Per-Agent Model Selector
In Pipeline Settings, expand the single model picker into a per-agent grid:
```
StoryForge:   [Google ▼] [gemini-2.5-pro ▼]     🧠 Reasoning
TestCraft:    [Groq ▼]   [llama-4-maverick ▼]   ⚡ Fast
GherkinGen:   [Groq ▼]   [llama-4-scout ▼]      ⚡ Fast
BrowserPilot: [Google ▼] [gemini-2.5-flash ▼]   👁️ Vision
CodeSmith:    [Anthropic ▼] [claude-sonnet ▼]   💻 Code
```

## Files
- `backend/app/models/request_models.py` — add AgentModelConfig
- `backend/app/agents/*.py` — accept per-agent model config
- `backend/app/services/pipeline_service.py` — pass per-agent models
- `frontend/app/dashboard/pipeline/components/input/ModelSelector.tsx` — per-agent UI

## Acceptance Criteria
- [ ] Each agent can use a different provider/model
- [ ] Smart defaults suggested based on task type
- [ ] Cost estimate shown in UI before running
- [ ] Vision-only models (Groq text models) blocked for BrowserPilot
- [ ] Config saved to run history for reproducibility""",
["phase-5-frontiers", "backend", "frontend", "new-feature"])

    issue(T, R, "[P5-3] Agent Builder UI — create, deploy, and manage custom agents",
"""## Problem
Every agent is hardcoded. Teams building specialized QA workflows (e.g., a HIPAA compliance checker, a payment flow specialist, a mobile-specific agent) have no way to create custom agents without editing source code.

## Solution
Agent Builder: a UI where users define custom agents with name, role, model, tools, instructions, response format, and deploy them as first-class pipeline members.

## AgentDefinition Schema
```python
class AgentDefinition(BaseModel):
    id: str                          # UUID
    name: str                        # "HIPAA Compliance Checker"
    slug: str                        # "hipaa-checker"
    description: str
    role: str                        # agent role/persona
    model_provider: str
    model_name: str
    tools: list[str]                 # from TOOL_REGISTRY
    instructions: list[str]          # system prompt lines
    response_format: Literal["markdown", "structured", "code"]
    output_schema: dict | None       # JSON Schema for structured output
    status: Literal["draft", "active", "archived"]
    created_at: datetime
    is_builtin: bool = False         # True for the 5 default agents

class AgentDefinition_TOOL_REGISTRY = {
    "jira":           "agno.tools.jira.JiraTools",
    "linear":         "agno.tools.linear_app.LinearTools",
    "web_search":     "agno.tools.websearch.WebSearchTools",
    "knowledge_base": "app.intelligence.knowledge_base.KBQueryTool",
    "browser":        "app.browser.browser_tools.BrowserUseTool",
    "reasoning":      "agno.tools.reasoning.ReasoningTools",
    "code_execution": "agno.tools.python.PythonTools",
    "file_tools":     "agno.tools.file.FileTools",
}
```

## build_agent_from_definition() Factory
```python
def build_agent_from_definition(defn: AgentDefinition) -> Agent:
    model = get_llm_instance(defn.model_provider, defn.model_name)
    tools = [TOOL_REGISTRY[t]() for t in defn.tools if t in TOOL_REGISTRY]
    return Agent(
        name=defn.name,
        model=model,
        tools=tools,
        instructions=defn.instructions,
        role=defn.role,
        response_model=build_response_model(defn.output_schema) if defn.output_schema else None,
    )
```

## UI Features
- **Visual editor**: drag-and-drop tool chips, instruction block editor
- **Live test panel**: send a sample prompt, see the response
- **Version history**: track changes to agent instructions
- **Share/export**: export agent definition as JSON, import from JSON
- **Clone builtin**: copy any of the 5 default agents as starting point

## Files
- `backend/app/services/agent_registry.py` (new)
- `backend/app/api/v1/agents.py` (new)
- `backend/app/db/models.py` — AgentDefinition table
- `frontend/app/dashboard/agents/page.tsx` (new)
- `frontend/app/dashboard/agents/components/AgentEditor.tsx` (new)
- `frontend/app/dashboard/agents/components/ToolSelector.tsx` (new)
- `frontend/app/dashboard/agents/components/TestPanel.tsx` (new)

## Acceptance Criteria
- [ ] User creates agent via UI, no code required
- [ ] Custom agent available in pipeline model picker
- [ ] Live test panel works before deployment
- [ ] All 8 built-in tools selectable
- [ ] Hot-reload: activate/deactivate without server restart""",
["phase-5-frontiers", "backend", "frontend", "agno", "new-feature"])

    issue(T, R, "[P5-4] Test Strategy Generator — given URL+domain, suggest full test plan",
"""## Problem
Junior QA engineers and non-QA developers don't know where to start. Given an app URL, what should they test? What's the right mix of unit/integration/e2e? Which areas are highest risk?

## Solution
A Test Strategy Generator that takes a URL + business domain → analyzes the app → produces a prioritized, comprehensive test strategy document.

## Input
```python
class StrategyRequest(BaseModel):
    url: str
    business_domain: Literal[
        "ecommerce", "fintech", "healthcare", "saas", "social",
        "education", "logistics", "enterprise", "other"
    ]
    team_size: Literal["solo", "small", "medium", "large"]
    current_coverage: str = ""   # optional: what they already test
    priority: Literal["speed", "coverage", "risk-based", "compliance"]
```

## Strategy Agent
```python
strategy_agent = Agent(
    model=reasoning_model,
    tools=[ReasoningTools(), SiteScoutTool(), WebSearchTools()],
    instructions=[
        "Analyze the provided URL using SiteScout to understand the app structure.",
        "Based on business domain and team size, recommend:",
        "1. Critical user journeys to test (prioritized)",
        "2. Test pyramid: unit/integration/e2e split recommendation",
        "3. Risk areas requiring most coverage",
        "4. Automation-first vs manual-first decision per area",
        "5. Specific WAIGenie pipeline configurations to use",
    ],
    response_model=TestStrategy,
)
```

## TestStrategy Output
```python
class TestStrategy(BaseModel):
    executive_summary: str
    critical_journeys: list[Journey]   # ordered by risk/importance
    test_pyramid: PyramidRecommendation
    risk_areas: list[RiskArea]
    automation_candidates: list[str]
    manual_only_areas: list[str]
    compliance_notes: list[str]        # GDPR, HIPAA, PCI-DSS if relevant
    estimated_coverage_hours: float
    waigenie_pipeline_configs: list[PipelineConfig]  # pre-filled settings
```

## UI: Strategy Page `/dashboard/strategy`
- Input form (URL + domain + team size + priority)
- Loading state with SiteScout progress
- Strategy report rendered as interactive document
- Each critical journey has a "Run Pipeline" button (pre-fills pipeline)
- Export to PDF / Confluence / Jira

## Files
- `backend/app/agents/strategy_agent.py` (new)
- `backend/app/api/v1/strategy.py` (new)
- `frontend/app/dashboard/strategy/page.tsx` (new)
- `frontend/app/dashboard/strategy/components/StrategyReport.tsx` (new)

## Acceptance Criteria
- [ ] Strategy generated within 60 seconds
- [ ] At least 5 critical journeys identified for any real app
- [ ] Risk areas specific to business domain (fintech → payment flows)
- [ ] "Run Pipeline" buttons pre-fill pipeline correctly
- [ ] Strategy exportable to PDF""",
["phase-5-frontiers", "backend", "frontend", "agno", "new-feature"])

    issue(T, R, "[P5-5] Confidential mode — route sensitive tests through local Ollama",
"""## Problem
Many enterprises and regulated industries (healthcare, fintech, legal) cannot send test data to external LLM APIs due to data sovereignty, compliance requirements, or proprietary data concerns.

## Solution
Confidential Mode: when enabled, all LLM calls are routed to a local Ollama instance. No data leaves the machine.

## Implementation
```python
class ConfidentialMode(BaseModel):
    enabled: bool = False
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"          # default local model
    vision_model: str = "llava"              # for browser execution
    override_all_agents: bool = True         # force ALL agents to Ollama
    excluded_agents: list[str] = []          # e.g., keep CodeSmith on cloud

# In pipeline_service.py
if settings.CONFIDENTIAL_MODE:
    provider, model = "Ollama", settings.OLLAMA_MODEL
    # Override all agent model selections
```

## Confidential Mode Indicator
- Red lock icon 🔒 in header when enabled
- Tooltip: "All data stays on your machine"
- Settings validation: test Ollama connectivity before enabling
- Performance warning: "Local models are 5-10x slower"

## Compliance Notes
- HIPAA: patient data never leaves local network
- GDPR: no personal data processed by third-party APIs
- PCI-DSS: payment test data stays local
- SOC2: audit log of all LLM calls (local or cloud)

## Model Recommendations by Use Case
```
Story + Test generation:  llama3.2 (good reasoning)
Gherkin generation:       qwen2.5 (fast, instruction-following)
Code generation:          codellama (code-specialized)
Browser execution:        llava (vision-capable)
```

## Files
- `backend/app/config/settings.py` — add ConfidentialMode settings
- `backend/app/services/pipeline_service.py` — confidential mode override
- `backend/app/api/v1/settings.py` — confidential mode toggle endpoint
- `frontend/app/layout/Header.tsx` — confidential mode indicator
- `frontend/app/dashboard/settings/page.tsx` — confidential mode section

## Acceptance Criteria
- [ ] Toggle in Settings enables confidential mode
- [ ] All pipeline LLM calls route to Ollama when enabled
- [ ] Connectivity test before enabling (Ollama must be running)
- [ ] Red lock icon visible in header when active
- [ ] Per-agent exception list (some agents can remain on cloud)
- [ ] Audit log of LLM call destinations""",
["phase-5-frontiers", "backend", "frontend", "new-feature"])

    print(f"\n\n=== All issues created on {R} ===")
    print("Phases covered:")
    print("  Phase 1 — Intelligence Core (P1-1 to P1-4): Structured outputs, Reasoning, Workflow 2.0, Teams")
    print("  Phase 2 — Better Browser   (P2-1 to P2-5): Profiles, Skills, Judge, Sessions, 2-phase Gherkin")
    print("  Phase 3 — Analysis Suite   (P3-1 to P3-3): Security/A11y/Visual, Element Inspector, DOM Proxy")
    print("  Phase 4 — Real-time        (P4-1 to P4-3): SSE Streaming, Run History, Analytics")
    print("  Phase 5 — New Frontiers    (P5-1 to P5-5): SiteScout, Multi-LLM, Agent Builder, Strategy, Confidential")
    print("\n  Total: 20 deep-dive issues")

if __name__ == "__main__":
    main()
