from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.browser_execution_service import browser_execution_service
from app.services.mcp_service import mcp_service
from app.api.deps import verify_api_key
import uuid
from datetime import datetime
import asyncio

router = APIRouter(dependencies=[Depends(verify_api_key)])

class BrowserExecutionRequest(BaseModel):
    test_script: str
    provider: str = "Google"
    model: str = "gemini-2.0-flash"

class BrowserExecutionResponse(BaseModel):
    task_id: str
    status: str
    results: Optional[Dict[str, Any]] = None
    test_script: str
    created_at: str

class BrowserExecutionStatusResponse(BaseModel):
    task_id: str
    status: str
    created_at: str
    updated_at: str

class BrowserExecutionResultsResponse(BaseModel):
    task_id: str
    status: str
    results: Dict[str, Any]
    test_script: str
    created_at: str
    completed_at: str

# In-memory storage for task tracking (in production, this would be a database)
execution_tasks: Dict[str, Dict[str, Any]] = {}

@router.post("/start", response_model=BrowserExecutionResponse)
async def start_browser_execution(request: BrowserExecutionRequest):
    """
    Start a browser execution task.

    Args:
        request (BrowserExecutionRequest): The request containing the test script

    Returns:
        BrowserExecutionResponse: Information about the started task
    """
    try:
        # Generate a unique task ID
        task_id = str(uuid.uuid4())

        # Package the task for MCP execution
        payload = {
            "test_script": request.test_script,
            "provider": request.provider,
            "model": request.model
        }

        # Submit the job to MCP service
        mcp_task_id = await mcp_service.submit_mcp_job("browser_use_execution", payload)

        # Store task information
        execution_tasks[task_id] = {
            "task_id": task_id,
            "mcp_task_id": mcp_task_id,
            "status": "started",
            "test_script": request.test_script,
            "provider": request.provider,
            "model": request.model,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        return BrowserExecutionResponse(
            task_id=task_id,
            status="started",
            test_script=request.test_script,
            created_at=execution_tasks[task_id]["created_at"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start browser execution: {str(e)}")

@router.get("/status/{task_id}", response_model=BrowserExecutionStatusResponse)
async def get_execution_status(task_id: str):
    """
    Get the status of a browser execution task.

    Args:
        task_id (str): The ID of the task to check

    Returns:
        BrowserExecutionStatusResponse: Status information for the task
    """
    if task_id not in execution_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = execution_tasks[task_id]

    # Check MCP task status
    if "mcp_task_id" in task:
        mcp_status = await mcp_service.get_job_status(task["mcp_task_id"])
        # Update local task status based on MCP status
        if mcp_status["status"] == "completed":
            task["status"] = "completed"
        elif mcp_status["status"] == "failed":
            task["status"] = "failed"
            task["error"] = mcp_status["error"]

    task["updated_at"] = datetime.now().isoformat()

    return BrowserExecutionStatusResponse(
        task_id=task["task_id"],
        status=task["status"],
        created_at=task["created_at"],
        updated_at=task["updated_at"]
    )

@router.get("/results/{task_id}", response_model=BrowserExecutionResultsResponse)
async def get_execution_results(task_id: str):
    """
    Get the results of a completed browser execution task.

    Args:
        task_id (str): The ID of the task to retrieve results for

    Returns:
        BrowserExecutionResultsResponse: Results of the completed task
    """
    if task_id not in execution_tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = execution_tasks[task_id]

    # Check MCP task status if not already completed
    if task["status"] not in ["completed", "failed"] and "mcp_task_id" in task:
        mcp_status = await mcp_service.get_job_status(task["mcp_task_id"])
        if mcp_status["status"] == "completed":
            task["status"] = "completed"
            task["results"] = mcp_status["result"]
            task["completed_at"] = datetime.now().isoformat()
        elif mcp_status["status"] == "failed":
            task["status"] = "failed"
            task["error"] = mcp_status["error"]
            task["completed_at"] = datetime.now().isoformat()

    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task is not completed yet")

    return BrowserExecutionResultsResponse(
        task_id=task["task_id"],
        status=task["status"],
        results=task.get("results", {}),
        test_script=task["test_script"],
        created_at=task["created_at"],
        completed_at=task.get("completed_at", datetime.now().isoformat())
    )

@router.get("/all")
async def get_all_executions():
    """
    Get all browser execution tasks.

    Returns:
        Dict: All execution tasks
    """
    return {"tasks": execution_tasks}
