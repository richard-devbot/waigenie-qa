from typing import Dict, Any, Optional
import threading
import time
from datetime import datetime

class TaskManager:
    """Thread-safe task manager for tracking pipeline execution status."""
    
    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
    
    def set_task_status(self, task_id: str, stage: str, data: Dict[str, Any]):
        """
        Set the status of a task with thread safety.
        
        Args:
            task_id (str): The unique task identifier
            stage (str): The current stage/status
            data (Dict[str, Any]): Task data including status, results, etc.
        """
        with self._lock:
            if task_id not in self._tasks:
                self._tasks[task_id] = {
                    "task_id": task_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            
            # Update the task with new data
            self._tasks[task_id].update(data)
            self._tasks[task_id]["updated_at"] = datetime.utcnow().isoformat()
            self._tasks[task_id]["current_stage"] = stage
            
            # Ensure we have a status field
            if "status" not in self._tasks[task_id]:
                if stage == "COMPLETED":
                    self._tasks[task_id]["status"] = "COMPLETED"
                elif stage == "FAILED" or stage == "ERROR":
                    self._tasks[task_id]["status"] = "FAILED"
                else:
                    self._tasks[task_id]["status"] = "RUNNING"
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a task.
        
        Args:
            task_id (str): The task ID to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: The task data or None if not found
        """
        with self._lock:
            return self._tasks.get(task_id)
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task from the manager.
        
        Args:
            task_id (str): The task ID to delete
            
        Returns:
            bool: True if task was deleted, False if not found
        """
        with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                return True
            return False
    
    def list_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        List all tasks in the manager.
        
        Returns:
            Dict[str, Dict[str, Any]]: All tasks
        """
        with self._lock:
            return self._tasks.copy()
    
    def cleanup_old_tasks(self, max_age_hours: int = 24):
        """
        Clean up tasks older than the specified age.
        
        Args:
            max_age_hours (int): Maximum age in hours for tasks to keep
        """
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        with self._lock:
            tasks_to_delete = []
            for task_id, task_data in self._tasks.items():
                try:
                    created_at = datetime.fromisoformat(task_data.get("created_at", ""))
                    if created_at.timestamp() < cutoff_time:
                        tasks_to_delete.append(task_id)
                except (ValueError, TypeError):
                    # If we can't parse the date, keep the task
                    continue
            
            for task_id in tasks_to_delete:
                del self._tasks[task_id]

# Create a singleton instance
task_manager = TaskManager()
