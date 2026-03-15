"""
Agno Team in coordinate mode — QA Master Orchestrator (Issue #25).
"""
from __future__ import annotations
import logging
from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.team import Team
from agno.team.team import TeamMode

from app.utils.model_factory import get_llm_instance
from app.models.agent_outputs import (
    EnhancedStory, TestCaseList, GherkinFeature, GeneratedCode
)

logger = logging.getLogger(__name__)


def create_qa_orchestrator(
    provider: str = "Google",
    model: str = "gemini-2.0-flash",
) -> Team:
    llm = get_llm_instance(provider, model, for_agno=True)

    story_forge = Agent(
        name="StoryForge",
        role="User Story Enhancer",
        model=llm,
        response_model=EnhancedStory,
        description="Transform rough user stories into detailed JIRA-style user stories with acceptance criteria.",
        instructions=[
            "Always extract clear acceptance criteria.",
            "Add testability considerations for QA teams.",
        ],
    )

    test_craft = Agent(
        name="TestCraft",
        role="Manual Test Case Generator",
        model=llm,
        response_model=TestCaseList,
        description="Convert enhanced user stories into comprehensive manual test cases.",
        instructions=[
            "Generate at least 5 test cases per acceptance criterion.",
            "Include test data, preconditions, and expected results.",
        ],
    )

    gherkin_gen = Agent(
        name="GherkinGen",
        role="Gherkin Scenario Writer",
        model=llm,
        response_model=GherkinFeature,
        description="Convert manual test cases into Gherkin scenarios ready for browser automation.",
        instructions=[
            "Every scenario must have a concrete entry_point_url.",
            "Follow Given-When-Then structure strictly.",
        ],
    )

    code_smith = Agent(
        name="CodeSmith",
        role="Test Automation Code Generator",
        model=llm,
        response_model=GeneratedCode,
        description="Generate production-ready test automation code from Gherkin scenarios.",
        instructions=[
            "Use Page Object Model pattern.",
            "Add proper waits and error handling.",
        ],
    )

    orchestrator = Team(
        members=[story_forge, test_craft, gherkin_gen, code_smith],
        name="QA Master Orchestrator",
        mode=TeamMode.coordinate,
        model=llm,
        description=dedent("""
            You are the QA Master Orchestrator. Coordinate specialist agents to produce
            end-to-end QA automation artifacts from a user story.

            Workflow:
            1. Delegate to StoryForge to enhance the raw user story.
            2. Delegate to TestCraft AND GherkinGen using the enhanced story.
            3. Delegate to CodeSmith with the Gherkin scenarios.
            4. Return all artifacts: enhanced story, test cases, Gherkin, code.
        """),
        instructions=[
            "Run TestCraft and GherkinGen in parallel where possible.",
            "Always include entry_point_url in Gherkin scenarios.",
            "Return a comprehensive summary with all stage outputs.",
        ],
    )

    return orchestrator
