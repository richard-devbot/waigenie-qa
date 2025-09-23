from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Tuple
from app.services.pipeline_service import pipeline_service

router = APIRouter()

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