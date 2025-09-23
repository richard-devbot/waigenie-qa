from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.test_case_service import test_case_service

router = APIRouter()

class TestCaseRequest(BaseModel):
    user_story: str
    context: Optional[str] = None
    provider: str = "Google"
    model: str = "gemini-2.0-flash"

class TestCaseResponse(BaseModel):
    test_cases: List[Dict[str, Any]]
    user_story: str
    context: Optional[str] = None

@router.post("/generate", response_model=TestCaseResponse)
async def generate_test_cases(request: TestCaseRequest):
    """
    Generate manual test cases from a user story or requirement.
    
    Args:
        request (TestCaseRequest): The request containing user story and context
        
    Returns:
        TestCaseResponse: Generated test cases
    """
    try:
        result = test_case_service.generate_test_cases(
            user_story=request.user_story,
            context=request.context,
            provider=request.provider,
            model=request.model
        )
        
        return TestCaseResponse(
            test_cases=result["test_cases"],
            user_story=result["user_story"],
            context=result["context"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate test cases: {str(e)}")