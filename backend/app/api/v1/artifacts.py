from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from pathlib import Path

router = APIRouter()

@router.get("/{session_id}/{artifact_type}/{agent_id}/{filename}")
async def get_agent_artifact(session_id: str, artifact_type: str, agent_id: str, filename: str):
    """
    Serve static files from the recordings directory associated with a specific parallel execution session.
    
    Args:
        session_id (str): The ID of the execution session
        artifact_type (str): Type of artifact (videos, network.traces, debug.traces)
        agent_id (str): The agent ID
        filename (str): The filename to serve
        
    Returns:
        FileResponse: The requested file
    """
    # Define the base recordings directory
    recordings_base = "./recordings"
    
    # Validate artifact type
    valid_artifact_types = ["videos", "network.traces", "debug.traces"]
    if artifact_type not in valid_artifact_types:
        raise HTTPException(status_code=400, detail="Invalid artifact type")
    
    # Construct the file path
    file_path = os.path.join(recordings_base, artifact_type, session_id, agent_id, filename)
    
    # Security check: Ensure the file is within the recordings directory
    file_path_obj = Path(file_path).resolve()
    recordings_path_obj = Path(recordings_base).resolve()
    
    if not str(file_path_obj).startswith(str(recordings_path_obj)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on file extension
    media_type = "application/octet-stream"
    if filename.endswith(".gif"):
        media_type = "image/gif"
    elif filename.endswith(".webm"):
        media_type = "video/webm"
    elif filename.endswith(".png"):
        media_type = "image/png"
    elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
        media_type = "image/jpeg"
    elif filename.endswith(".har"):
        media_type = "application/json"
    elif filename.endswith(".json"):
        media_type = "application/json"
    
    return FileResponse(file_path, media_type=media_type, filename=filename)

@router.get("/{session_id}/{artifact_type}/{filename}")
async def get_session_artifact(session_id: str, artifact_type: str, filename: str):
    """
    Serve static files from the recordings directory associated with a specific session (simplified path).
    
    Args:
        session_id (str): The ID of the session
        artifact_type (str): Type of artifact (videos, network.traces, debug.traces)
        filename (str): The filename to serve
        
    Returns:
        FileResponse: The requested file
    """
    # Define the base recordings directory
    recordings_base = "./recordings"
    
    # Validate artifact type
    valid_artifact_types = ["videos", "network.traces", "debug.traces"]
    if artifact_type not in valid_artifact_types:
        raise HTTPException(status_code=400, detail="Invalid artifact type")
    
    # Construct the file path
    file_path = os.path.join(recordings_base, artifact_type, session_id, filename)
    
    # Security check: Ensure the file is within the recordings directory
    file_path_obj = Path(file_path).resolve()
    recordings_path_obj = Path(recordings_base).resolve()
    
    if not str(file_path_obj).startswith(str(recordings_path_obj)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type based on file extension
    media_type = "application/octet-stream"
    if filename.endswith(".gif"):
        media_type = "image/gif"
    elif filename.endswith(".webm"):
        media_type = "video/webm"
    elif filename.endswith(".png"):
        media_type = "image/png"
    elif filename.endswith(".jpg") or filename.endswith(".jpeg"):
        media_type = "image/jpeg"
    elif filename.endswith(".har"):
        media_type = "application/json"
    elif filename.endswith(".json"):
        media_type = "application/json"
    
    return FileResponse(file_path, media_type=media_type, filename=filename)

@router.get("/{session_id}/{artifact_type}/{agent_id}/")
async def list_agent_artifacts(session_id: str, artifact_type: str, agent_id: str):
    """
    List all artifacts for a specific agent in a session.
    
    Args:
        session_id (str): The ID of the execution session
        artifact_type (str): Type of artifact (videos, network.traces, debug.traces)
        agent_id (str): The agent ID
        
    Returns:
        dict: List of available artifacts
    """
    # Define the base recordings directory
    recordings_base = "./recordings"
    
    # Validate artifact type
    valid_artifact_types = ["videos", "network.traces", "debug.traces"]
    if artifact_type not in valid_artifact_types:
        raise HTTPException(status_code=400, detail="Invalid artifact type")
    
    # Construct the directory path
    dir_path = os.path.join(recordings_base, artifact_type, session_id, agent_id)
    
    # Security check: Ensure the directory is within the recordings directory
    dir_path_obj = Path(dir_path).resolve()
    recordings_path_obj = Path(recordings_base).resolve()
    
    if not str(dir_path_obj).startswith(str(recordings_path_obj)):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if directory exists
    if not os.path.exists(dir_path):
        return {"artifacts": []}
    
    # List all files in the directory
    try:
        artifacts = []
        for file_path in Path(dir_path).iterdir():
            if file_path.is_file():
                artifacts.append({
                    "name": file_path.name,
                    "path": str(file_path.relative_to(recordings_base)),
                    "size": file_path.stat().st_size,
                    "modified": file_path.stat().st_mtime
                })
        return {"artifacts": artifacts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing artifacts: {str(e)}")