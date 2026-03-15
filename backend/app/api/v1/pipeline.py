import asyncio

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Tuple
from app.services.pipeline_service import pipeline_service
from app.workflows.qa_pipeline import QAPipeline
from app.agents.orchestrator import create_qa_orchestrator
from app.api.deps import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])

class PipelineStartRequest(BaseModel):
    raw_story: str
    framework: str
    context: Optional[str] = None
    provider: Optional[str] = "Google"
    model: Optional[str] = "gemini-2.0-flash"
    browser_name: Optional[str] = "chrome"
    browser_executable_path: Optional[str] = None
    browser_resolution: Optional[Tuple[int, int]] = None
    # New browser configuration options
    vision_enabled: bool = True
    cdp_port: Optional[int] = None

class PipelineStartResponse(BaseModel):
    task_id: str
    message: str

class PipelineStatusResponse(BaseModel):
    task_id: str
    status: str
    data: dict

@router.post("/start", response_model=PipelineStartResponse)
async def start_pipeline(request: PipelineStartRequest):
    """
    Start the end-to-end pipeline process.

    Args:
        request (PipelineStartRequest): The request containing user story and framework

    Returns:
        PipelineStartResponse: The task ID for tracking the pipeline
    """
    try:
        task_id = await pipeline_service.start_pipeline(
            raw_story=request.raw_story,
            framework=request.framework,
            context=request.context,
            provider=request.provider,
            model=request.model,
            browser_name=request.browser_name,
            browser_executable_path=request.browser_executable_path,
            browser_resolution=request.browser_resolution,
            vision_enabled=request.vision_enabled,
            cdp_port=request.cdp_port
        )

        return PipelineStartResponse(
            task_id=task_id,
            message="Pipeline started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start pipeline: {str(e)}")

@router.get("/status/{task_id}")
async def get_pipeline_status(task_id: str):
    """
    Get the current status of a pipeline task.

    Args:
        task_id (str): The task ID to check

    Returns:
        Dict: The complete task object with all data including results
    """
    task = pipeline_service.get_pipeline_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Return the entire task object to ensure frontend receives all results
    return task

@router.post("/workflow")
async def start_workflow_pipeline(request: PipelineStartRequest):
    """Start pipeline using Agno Workflow 2.0 with parallel stages 2+3."""
    provider = request.provider or "Google"
    model = request.model or "gemini-2.0-flash"
    pipeline = QAPipeline()
    final = await asyncio.to_thread(
        pipeline.run,
        raw_story=request.raw_story,
        framework=request.framework,
        context=request.context,
        provider=provider,
        model=model,
    )
    return {"status": "completed", "data": final}


@router.post("/orchestrate")
async def start_orchestrated_pipeline(request: PipelineStartRequest):
    """
    Start pipeline using Agno Team coordinate mode orchestrator (Issue #25).
    Delegates to StoryForge, TestCraft, GherkinGen, and CodeSmith specialist agents.
    """
    try:
        team = create_qa_orchestrator(
            provider=request.provider or "Google",
            model=request.model or "gemini-2.0-flash",
        )
    except Exception as e:
        return {"status": "error", "error": f"Failed to create orchestrator: {str(e)}", "data": {}}

    prompt = f"""
User Story: {request.raw_story}
Framework: {request.framework}
Context: {request.context or 'No additional context'}

Please run the full QA pipeline and return all artifacts.
"""
    try:
        response = await asyncio.to_thread(team.run, prompt)
    except Exception as e:
        return {"status": "error", "error": str(e), "data": {}}

    content = response.content if hasattr(response, "content") else str(response)
    return {
        "status": "completed",
        "data": content if isinstance(content, dict) else {"raw": str(content)},
    }


# New endpoint to get detailed status
@router.get("/detailed-status/{task_id}")
async def get_detailed_pipeline_status(task_id: str):
    """
    Get the detailed status of a pipeline task.

    Args:
        task_id (str): The task ID to check

    Returns:
        Dict: The detailed task status information
    """
    task = pipeline_service.get_pipeline_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
