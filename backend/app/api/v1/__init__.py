from fastapi import APIRouter
from app.api.v1 import pipeline, story, tests, gherkin, code, execute, debug, artifacts, browsers

api_router = APIRouter()
api_router.include_router(pipeline.router, prefix="/pipeline")
api_router.include_router(story.router, prefix="/story")
api_router.include_router(tests.router, prefix="/tests")
api_router.include_router(gherkin.router, prefix="/gherkin")
api_router.include_router(code.router, prefix="/code")
api_router.include_router(execute.router, prefix="/execute")
api_router.include_router(debug.router, prefix="/debug")
api_router.include_router(artifacts.router, prefix="/artifacts")
api_router.include_router(browsers.router, prefix="/browsers")