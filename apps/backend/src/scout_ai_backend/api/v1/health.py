from fastapi import APIRouter

from scout_ai_backend.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, object]:
    settings = get_settings()
    return {"status": "ok", "cors_origins": settings.cors_origins, "ai_provider": settings.ai_provider}
