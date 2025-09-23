from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.models.request_models import StoryEnhanceRequest
from app.models.response_models import StoryEnhanceResponse
from app.api.deps import verify_api_key
from app.services.story_service import StoryService

router = APIRouter()
story_service = StoryService()

@router.post("/enhance", response_model=StoryEnhanceResponse)
async def enhance_user_story(request: StoryEnhanceRequest):
    """
    Enhance a raw user story using AI agents
    """
    try:
        # Verify API key
        # Consume the generator properly
        for _ in verify_api_key(request.provider):
            pass
        
        # Validate input
        if not story_service.validate_input(request.raw_story):
            raise HTTPException(status_code=400, detail="User story cannot be empty")
        
        # Implement story enhancement logic using the service
        result = await story_service.enhance_user_story(
            raw_story=request.raw_story,
            provider=request.provider,
            model=request.model
        )
        
        return StoryEnhanceResponse(
            enhanced_story=result["enhanced_story"],
            metadata=result["metadata"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enhancing story: {str(e)}")