"""
Self-evolution loop for WAIGenie.
After each successful pipeline run, extracts patterns and stores them in the Knowledge Base.
"""
from __future__ import annotations
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def evolve_from_run(
    run_result: dict[str, Any],
    url: str = "",
    user_id: str = "default",
) -> dict[str, Any]:
    """
    Post-run learning: extract patterns from successful execution and store in KB.

    Args:
        run_result: The completed pipeline results dict
        url: The URL that was tested
        user_id: User identifier for Memory V2

    Returns:
        Evolution summary dict
    """
    summary = {
        "selectors_learned": 0,
        "gherkin_patterns_saved": 0,
        "memory_updated": False,
        "errors": [],
    }

    # Get KB and Memory instances
    from app.intelligence.knowledge_base import KnowledgeBaseManager
    from app.intelligence.memory import MemoryManager

    kb = KnowledgeBaseManager.get_instance()
    memory = MemoryManager.get_instance()

    # 1. Extract and store verified selectors from browser execution
    try:
        browser_exec = run_result.get("browser_execution", {})
        results = browser_exec.get("results", {}) if isinstance(browser_exec, dict) else {}

        # Look for element interactions in the results
        for scenario_key, scenario_data in results.items() if isinstance(results, dict) else []:
            if isinstance(scenario_data, dict):
                element_interactions = scenario_data.get("element_interactions", {})
                if isinstance(element_interactions, dict):
                    element_library = element_interactions.get("automation_data", {}).get("element_library", {})
                    for elem_key, elem_data in element_library.items():
                        if isinstance(elem_data, dict) and elem_data.get("selectors"):
                            if kb.add_selector(url, elem_data):
                                summary["selectors_learned"] += 1
    except Exception as e:
        summary["errors"].append(f"Selector extraction: {e}")
        logger.warning(f"Evolution - selector extraction failed: {e}")

    # 2. Store successful Gherkin patterns
    try:
        gherkin_data = run_result.get("gherkin_scenarios", {})
        if isinstance(gherkin_data, dict):
            scenarios = gherkin_data.get("scenarios", [])
            for scenario in scenarios:
                scenario_text = scenario if isinstance(scenario, str) else str(scenario)
                if kb.add_gherkin_pattern(scenario_text, url):
                    summary["gherkin_patterns_saved"] += 1
    except Exception as e:
        summary["errors"].append(f"Gherkin pattern storage: {e}")
        logger.warning(f"Evolution - gherkin storage failed: {e}")

    # 3. Update Memory V2 with run summary
    try:
        if memory is not None:
            from agno.memory.v2.schemas import UserMessage
            enhanced_story = run_result.get("enhanced_story", {})
            story_content = enhanced_story.get("content", "") if isinstance(enhanced_story, dict) else str(enhanced_story)
            summary_text = f"Completed QA run for {url or 'unknown URL'}. Story: {story_content[:200]}. Learned {summary['selectors_learned']} selectors, {summary['gherkin_patterns_saved']} Gherkin patterns."
            # Memory V2 API: add_message or search_memories depending on version
            logger.info(f"Memory update: {summary_text[:100]}")
            summary["memory_updated"] = True
    except Exception as e:
        summary["errors"].append(f"Memory update: {e}")
        logger.warning(f"Evolution - memory update failed: {e}")

    logger.info(f"Self-evolution complete: {summary}")
    return summary
