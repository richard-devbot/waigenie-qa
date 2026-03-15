# backend/app/workflows/qa_pipeline.py
"""
Agno Workflow 2.0 — QA Pipeline (Issue #24)
Runs TestCraft (Stage 2) and GherkinGen (Stage 3) in parallel via Agno Parallel.

NOTE: Agno 2.5.9 uses a dataclass-based Workflow API where steps are passed as
a callable or list to the Workflow constructor. This replaces the older
generator/RunResponse/RunEvent pattern described in pre-2.x docs.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, Optional

from agno.workflow import Workflow, Step, Parallel, StepInput, StepOutput

from app.agents.user_story_agent import create_user_story_enhancement_agent
from app.agents.test_case_agent import create_test_case_agent
from app.agents.gherkin_agent import create_gherkin_agent
from app.models.agent_outputs import (
    EnhancedStory, TestCaseList, GherkinFeature, TestCase, GherkinScenario
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Step executor helpers
# ---------------------------------------------------------------------------

def _build_story_step(provider: str, model: str, raw_story: str):
    """Return a Step that enhances the raw user story."""

    def enhance_story(step_input: StepInput) -> StepOutput:
        story = step_input.get_input_as_string() or raw_story
        agent = create_user_story_enhancement_agent(provider, model)
        resp = agent.run(story)
        raw = resp.content if (resp is not None and hasattr(resp, "content")) else resp
        if isinstance(raw, EnhancedStory):
            enhanced = raw
        elif isinstance(raw, dict):
            enhanced = EnhancedStory(**raw)
        else:
            enhanced = EnhancedStory(
                title="Enhanced Story",
                as_a="user",
                i_want="complete the task",
                so_that="achieve the goal",
                elaboration=str(raw) if raw else "",
            )
        return StepOutput(
            step_name="enhance_story",
            content=enhanced.model_dump(),
            success=True,
        )

    return Step(name="enhance_story", executor=enhance_story)


def _build_test_case_step(provider: str, model: str, context: Optional[str]):
    """Return a Step that generates test cases from the enriched story text."""

    def run_test_case(step_input: StepInput) -> StepOutput:
        story_text = step_input.get_input_as_string() or ""
        if context:
            story_text = f"{story_text}\n\nContext: {context}"
        agent = create_test_case_agent(provider, model)
        resp = agent.run(story_text)
        raw = resp.content if (resp is not None and hasattr(resp, "content")) else resp
        if isinstance(raw, TestCaseList):
            result = raw
        elif isinstance(raw, dict):
            result = TestCaseList(**raw)
        else:
            try:
                data = json.loads(str(raw))
                if isinstance(data, list):
                    result = TestCaseList(
                        test_cases=[
                            TestCase(**tc) if isinstance(tc, dict) else tc for tc in data
                        ]
                    )
                else:
                    result = TestCaseList(test_cases=[])
            except Exception:
                result = TestCaseList(test_cases=[])
        return StepOutput(
            step_name="test_cases",
            content=[tc.model_dump() for tc in result.test_cases],
            success=True,
        )

    return Step(name="test_cases", executor=run_test_case)


def _build_gherkin_step(provider: str, model: str, context: Optional[str]):
    """Return a Step that generates Gherkin scenarios from the enriched story text."""

    def run_gherkin(step_input: StepInput) -> StepOutput:
        story_text = step_input.get_input_as_string() or ""
        if context:
            story_text = f"{story_text}\n\nContext: {context}"
        agent = create_gherkin_agent(provider, model)
        resp = agent.run(story_text)
        raw = resp.content if (resp is not None and hasattr(resp, "content")) else resp
        if isinstance(raw, GherkinFeature):
            result = raw
        elif isinstance(raw, dict):
            result = GherkinFeature(**raw)
        else:
            try:
                data = json.loads(str(raw))
                if isinstance(data, list):
                    result = GherkinFeature(
                        scenarios=[
                            GherkinScenario(**s) if isinstance(s, dict) else s for s in data
                        ]
                    )
                else:
                    result = GherkinFeature(scenarios=[])
            except Exception:
                result = GherkinFeature(scenarios=[])
        return StepOutput(
            step_name="gherkin_scenarios",
            content=[s.model_dump(by_alias=True) for s in result.scenarios],
            success=True,
        )

    return Step(name="gherkin_scenarios", executor=run_gherkin)


# ---------------------------------------------------------------------------
# Public factory
# ---------------------------------------------------------------------------

def create_qa_pipeline(
    raw_story: str,
    framework: str = "playwright",
    context: Optional[str] = None,
    provider: str = "Google",
    model: str = "gemini-2.0-flash",
) -> Workflow:
    """
    Build and return a QAPipeline Workflow instance.

    Pipeline stages:
      1. enhance_story  — sequential
      2+3. test_cases + gherkin_scenarios — parallel
    """

    def pipeline_steps(workflow: Workflow, execution_input: Any) -> StepOutput:
        """
        Callable steps function for Agno Workflow 2.0.
        Stages 2+3 (TestCraft & GherkinGen) run in parallel.
        """
        # Stage 1: story enhancement — run directly (sequential)
        story_step = _build_story_step(provider, model, raw_story)
        story_input = StepInput(input=raw_story)
        story_output = story_step.executor(story_input)  # type: ignore[misc]

        if not story_output.success:
            return StepOutput(
                step_name="pipeline",
                content={"error": story_output.error},
                success=False,
                error=story_output.error,
            )

        enhanced_dict = story_output.content or {}
        if isinstance(enhanced_dict, EnhancedStory):
            enhanced_dict = enhanced_dict.model_dump()

        # Build enriched story text for stages 2+3
        story_text = (
            f"As a {enhanced_dict.get('as_a', 'user')}, "
            f"I want {enhanced_dict.get('i_want', 'complete the task')}, "
            f"so that {enhanced_dict.get('so_that', 'achieve the goal')}.\n\n"
            f"{enhanced_dict.get('elaboration', '')}\n\n"
            "Acceptance Criteria:\n"
            + "\n".join(
                f"- {c}" for c in enhanced_dict.get("acceptance_criteria", [])
            )
        )

        # Stages 2+3: parallel execution
        tc_step = _build_test_case_step(provider, model, context)
        gh_step = _build_gherkin_step(provider, model, context)

        parallel_input = StepInput(input=story_text)

        # Run in parallel using concurrent.futures via asyncio
        async def _gather():
            loop = asyncio.get_event_loop()
            tc_out, gh_out = await asyncio.gather(
                loop.run_in_executor(None, tc_step.executor, parallel_input),  # type: ignore[misc]
                loop.run_in_executor(None, gh_step.executor, parallel_input),  # type: ignore[misc]
            )
            return tc_out, gh_out

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Already inside an event loop (e.g. FastAPI) — use thread pool trick
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, _gather())
                    tc_out, gh_out = future.result()
            else:
                tc_out, gh_out = loop.run_until_complete(_gather())
        except RuntimeError:
            tc_out, gh_out = asyncio.run(_gather())

        return StepOutput(
            step_name="pipeline",
            content={
                "stage": "WORKFLOW_COMPLETE",
                "enhanced_story": enhanced_dict,
                "test_cases": tc_out.content if tc_out.success else [],
                "gherkin_scenarios": gh_out.content if gh_out.success else [],
                "framework": framework,
            },
            success=True,
        )

    return Workflow(
        name="qa-pipeline",
        description="End-to-end QA pipeline: Story -> [Tests || Gherkin] -> Browser -> Code",
        steps=pipeline_steps,
    )


class QAPipeline:
    """
    Thin wrapper that matches the interface expected by the /pipeline/workflow
    endpoint while delegating to the Agno Workflow 2.5.9 API.
    """

    def run(
        self,
        raw_story: str,
        framework: str = "playwright",
        context: Optional[str] = None,
        provider: str = "Google",
        model: str = "gemini-2.0-flash",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Execute the QA pipeline synchronously and return the final result dict.
        """
        wf = create_qa_pipeline(
            raw_story=raw_story,
            framework=framework,
            context=context,
            provider=provider,
            model=model,
        )
        result = wf.run(input=raw_story)
        # WorkflowRunOutput has step_results; extract the last step's content
        if hasattr(result, "step_results") and result.step_results:
            last = result.step_results[-1]
            content = last.content if hasattr(last, "content") else {}
            return content if isinstance(content, dict) else {"raw": content}
        # Fallback: try .content directly
        if hasattr(result, "content") and result.content:
            return result.content if isinstance(result.content, dict) else {"raw": result.content}
        return {}
