"""Structured Pydantic output models for all 5 WAIGenie agents (Issue #22)."""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union


# ── P1-1a: UserStory Agent ──────────────────────────────────────────────────

class AcceptanceCriterion(BaseModel):
    index: int
    text: str

class EnhancedStory(BaseModel):
    title: str = Field(..., description="Short story title")
    as_a: str = Field(..., description="User role/persona")
    i_want: str = Field(..., description="What the user wants")
    so_that: str = Field(..., description="Business value")
    elaboration: str = Field(..., description="Context and details")
    acceptance_criteria: List[str] = Field(default_factory=list)
    implementation_notes: List[str] = Field(default_factory=list)
    testability_considerations: List[str] = Field(default_factory=list)
    related_stories: List[str] = Field(default_factory=list)


# ── P1-1b: TestCase Agent ───────────────────────────────────────────────────

class TestCase(BaseModel):
    id: str = Field(..., description="e.g. TC_US_001_01")
    title: str
    description: str
    pre_conditions: str = ""
    steps: List[str] = Field(default_factory=list)
    expected_results: List[str] = Field(default_factory=list)
    test_data: str = ""
    priority: str = "Medium"
    test_type: str = "Functional"
    status: str = "Not Executed"
    post_conditions: str = ""
    environment: str = ""
    automation_status: str = "Not Automated"
    user_story_id: str = ""
    acceptance_criterion_ref: str = ""
    tags: List[str] = Field(default_factory=list)
    severity: str = "Medium"

class TestCaseList(BaseModel):
    test_cases: List[TestCase]
    total_count: int = Field(default=0)

    def model_post_init(self, __context: Any) -> None:
        if self.total_count == 0:
            self.total_count = len(self.test_cases)


# ── P1-1c: Gherkin Agent ────────────────────────────────────────────────────

class GherkinScenario(BaseModel):
    title: str
    tags: List[str] = Field(default_factory=list)
    feature: str = ""
    given: Union[str, List[str]] = ""
    when: Union[str, List[str]] = ""
    then: Union[str, List[str]] = ""
    and_steps: List[str] = Field(default_factory=list, alias="and")
    but: str = ""
    background: str = ""
    entry_point_url: str = ""

    model_config = {"populate_by_name": True}

class GherkinFeature(BaseModel):
    scenarios: List[GherkinScenario]
    feature_name: str = ""
    scenario_count: int = Field(default=0)

    def model_post_init(self, __context: Any) -> None:
        if self.scenario_count == 0:
            self.scenario_count = len(self.scenarios)


# ── P1-1d: Code Generation Agent ────────────────────────────────────────────

class GeneratedCode(BaseModel):
    framework: str
    language: str = ""
    code: str
    file_name: str = "test_automation.py"
    imports: List[str] = Field(default_factory=list)
    notes: str = ""


# ── P1-1e: Browser Execution Agent (result wrapper) ─────────────────────────

class StepResult(BaseModel):
    step: str
    action: str = ""
    selector: str = ""
    passed: bool = True
    error: str = ""
    screenshot_path: str = ""

class ScenarioResult(BaseModel):
    scenario_title: str
    passed: bool
    steps: List[StepResult] = Field(default_factory=list)
    duration_seconds: float = 0.0
    error: str = ""
    gif_path: str = ""

class BrowserExecutionResult(BaseModel):
    results: List[ScenarioResult] = Field(default_factory=list)
    total_scenarios: int = 0
    passed: int = 0
    failed: int = 0
    raw_response: str = ""
