from fastapi import APIRouter

from scout_ai_backend.api.v1 import health, matches

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(matches.router)
