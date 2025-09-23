#!/usr/bin/env python3
"""Simple verification script to check artifact paths and structure."""

import os
import json
from pathlib import Path

def verify_artifact_structure():
    """Verify the artifact directory structure."""
    
    # Define the base recordings directory
    recordings_base = "./recordings"
    
    print("Verifying artifact directory structure...")
    
    # Check if recordings directory exists
    if not os.path.exists(recordings_base):
        print(f"Recordings directory does not exist: {recordings_base}")
        return False
    
    # Check subdirectories
    artifact_types = ["videos", "network.traces", "debug.traces"]
    for artifact_type in artifact_types:
        path = os.path.join(recordings_base, artifact_type)
        if os.path.exists(path):
            print(f"  {artifact_type}: EXISTS")
        else:
            print(f"  {artifact_type}: MISSING")
    
    # Check if we can create a test directory structure
    test_session = "test_session_001"
    test_agent = "agent_0"
    
    # Create test paths
    test_video_dir = os.path.join(recordings_base, "videos", test_session, test_agent)
    test_traces_dir = os.path.join(recordings_base, "debug.traces", test_session, test_agent)
    test_har_path = os.path.join(recordings_base, "network.traces", test_session, f"{test_agent}.har")
    
    try:
        # Create directories
        Path(test_video_dir).mkdir(parents=True, exist_ok=True)
        Path(test_traces_dir).mkdir(parents=True, exist_ok=True)
        Path(os.path.dirname(test_har_path)).mkdir(parents=True, exist_ok=True)
        
        # Create a dummy GIF file
        dummy_gif_path = os.path.join(test_video_dir, "execution.gif")
        with open(dummy_gif_path, "w") as f:
            f.write("Dummy GIF content")
        
        # Create a dummy HAR file
        with open(test_har_path, "w") as f:
            json.dump({"log": {"version": "1.2", "creator": {"name": "test", "version": "1.0"}}}, f)
        
        print(f"Created test artifact structure:")
        print(f"  GIF: {dummy_gif_path}")
        print(f"  HAR: {test_har_path}")
        print(f"  Video dir: {test_video_dir}")
        print(f"  Traces dir: {test_traces_dir}")
        
        # Verify creation
        if os.path.exists(dummy_gif_path):
            print("  GIF file: CREATED")
        else:
            print("  GIF file: FAILED")
            
        if os.path.exists(test_har_path):
            print("  HAR file: CREATED")
        else:
            print("  HAR file: FAILED")
            
        return True
        
    except Exception as e:
        print(f"Error creating test structure: {e}")
        return False

def verify_frontend_paths():
    """Verify the frontend artifact paths."""
    
    print("\nVerifying frontend artifact paths...")
    
    # Example session and agent data
    session_id = "parallel_execution_20241201_120000"
    agent_id = 0
    
    # Expected paths
    gif_path = f"./recordings/videos/{session_id}/agent_{agent_id}/execution.gif"
    har_path = f"./recordings/network.traces/{session_id}/agent_{agent_id}.har"
    video_dir = f"./recordings/videos/{session_id}/agent_{agent_id}"
    traces_dir = f"./recordings/debug.traces/{session_id}/agent_{agent_id}"
    
    print(f"Expected artifact paths:")
    print(f"  GIF: {gif_path}")
    print(f"  HAR: {har_path}")
    print(f"  Video dir: {video_dir}")
    print(f"  Traces dir: {traces_dir}")
    
    # Expected API endpoints
    gif_api = f"/api/v1/artifacts/{session_id}/videos/agent_{agent_id}/execution.gif"
    har_api = f"/api/v1/artifacts/{session_id}/network.traces/agent_{agent_id}.har"
    
    print(f"Expected API endpoints:")
    print(f"  GIF: {gif_api}")
    print(f"  HAR: {har_api}")

if __name__ == "__main__":
    print("Artifact verification script")
    print("=" * 40)
    
    # Verify directory structure
    verify_artifact_structure()
    
    # Verify frontend paths
    verify_frontend_paths()
    
    print("\nVerification complete!")