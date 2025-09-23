import asyncio
import uuid
from typing import Dict, Any, Optional
import json
import os
from datetime import datetime
import sys
import platform

class MCPService:
    """Service for simulating MCP server interactions for browser execution tasks."""
    
    def __init__(self):
        """Initialize the MCP service."""
        # Set event loop policy for Windows to avoid subprocess issues
        if platform.system() == "Windows":
            if sys.version_info >= (3, 8):
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            else:
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.max_concurrent_jobs = 5  # Limit concurrent jobs to prevent resource exhaustion
        self.current_jobs = 0
    
    async def submit_mcp_job(self, task_type: str, payload: dict) -> str:
        """
        Submit a job to the MCP service.
        
        Args:
            task_type: Type of task ('agno_agent_run' or 'browser_use_execution')
            payload: Data needed for the task
            
        Returns:
            str: Task ID for polling
        """
        # Wait if we've reached the maximum concurrent jobs
        while self.current_jobs >= self.max_concurrent_jobs:
            await asyncio.sleep(1)
        
        task_id = str(uuid.uuid4())
        
        # Store the job
        self.jobs[task_id] = {
            "task_id": task_id,
            "task_type": task_type,
            "payload": payload,
            "status": "submitted",
            "created_at": datetime.now().isoformat(),
            "result": None,
            "error": None
        }
        
        # Process the job asynchronously
        asyncio.create_task(self._process_job(task_id))
        
        return task_id
    
    async def _process_job(self, task_id: str):
        """Process a job asynchronously."""
        if task_id not in self.jobs:
            return
            
        # Increment current jobs counter
        self.current_jobs += 1
        
        job = self.jobs[task_id]
        job["status"] = "processing"
        
        try:
            if job["task_type"] == "browser_use_parallel_execution":
                # Process parallel browser execution task with tab management
                from app.services.browser_execution_service import browser_execution_service
                
                test_scripts = job["payload"].get("test_scripts", [])
                provider = job["payload"].get("provider", "Google")
                model = job["payload"].get("model", "gemini-2.0-flash")
                browser_name = job["payload"].get("browser_name", "chrome")
                browser_executable_path = job["payload"].get("browser_executable_path")
                browser_resolution = job["payload"].get("browser_resolution")
                vision_enabled = job["payload"].get("vision_enabled", True)
                cdp_port = job["payload"].get("cdp_port")
                
                # Execute the browser tests in parallel with tab management
                result = await browser_execution_service.execute_parallel_browser_tests(
                    test_scripts=test_scripts,
                    provider=provider,
                    model=model,
                    browser_name=browser_name,
                    browser_executable_path=browser_executable_path,
                    browser_resolution=browser_resolution,
                    vision_enabled=vision_enabled,
                    cdp_port=cdp_port
                )
                job["result"] = result
                job["status"] = "completed"
            elif job["task_type"] == "browser_use_execution":
                # Process single browser execution task
                from app.services.browser_execution_service import browser_execution_service
                
                test_script = job["payload"].get("test_script", "")
                provider = job["payload"].get("provider", "Google")
                model = job["payload"].get("model", "gemini-2.0-flash")
                
                # Execute the browser test
                result = await browser_execution_service.execute_browser_test(
                    test_script=test_script,
                    provider=provider,
                    model=model
                )
                job["result"] = result
                job["status"] = "completed"
            elif job["task_type"] == "agno_agent_run":
                # Process AGNO agent task
                result = await self._execute_agno_task(job["payload"])
                job["result"] = result
                job["status"] = "completed"
            else:
                raise ValueError(f"Unknown task type: {job['task_type']}")
        except Exception as e:
            job["error"] = str(e)
            job["status"] = "failed"
        finally:
            # Decrement current jobs counter
            self.current_jobs -= 1
    
    async def _execute_agno_task(self, payload: dict) -> Dict[str, Any]:
        """
        Execute an AGNO agent task.
        
        Args:
            payload: Task payload containing agent configuration
            
        Returns:
            Dict[str, Any]: Agent results
        """
        # This is where we would actually execute the AGNO agent task
        # For now, we'll return a mock result
        return {
            "status": "completed",
            "result": "Task completed successfully",
            "output": "Generated content from AGNO agent"
        }
    
    async def get_job_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a job.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Dict[str, Any]: Job status information
        """
        if task_id not in self.jobs:
            return {"status": "not_found", "error": "Task not found"}
        
        job = self.jobs[task_id]
        return {
            "task_id": job["task_id"],
            "status": job["status"],
            "task_type": job["task_type"],
            "created_at": job["created_at"],
            "result": job["result"],
            "error": job["error"]
        }

# Global instance
mcp_service = MCPService()