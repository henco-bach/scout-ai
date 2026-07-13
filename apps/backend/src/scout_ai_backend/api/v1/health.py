from typing import Annotated
from uuid import UUID

import cv2
import numpy as np
from fastapi import APIRouter, Depends, HTTPException

from scout_ai_backend.api.deps import get_match_service
from scout_ai_backend.core.config import get_settings
from scout_ai_backend.domain.services.match_service import MatchService
from scout_ai_backend.infrastructure.vision.pipeline import _detect

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, object]:
    settings = get_settings()
    return {"status": "ok", "cors_origins": settings.cors_origins, "ai_provider": settings.ai_provider}


@router.get("/debug/frame-check/{match_id}")
async def frame_check(
    match_id: UUID,
    service: Annotated[MatchService, Depends(get_match_service)],
) -> dict[str, object]:
    """Temporary diagnostic: opens a match's stored video in this exact
    runtime environment, reads the first frame, and runs real-time
    detection on it, to distinguish a decode problem in this container
    from a genuine detection problem."""
    match = await service.get_match(match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    settings = get_settings()
    cap = cv2.VideoCapture(match.video_path)
    opened = cap.isOpened()
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    ok, frame = cap.read()
    cap.release()

    if not ok:
        return {"opened": opened, "fps": fps, "frame_count": frame_count, "frame_read_ok": False}

    detections = _detect(
        frame,
        roboflow_api_key=settings.roboflow_api_key,
        roboflow_model_id=settings.roboflow_model_id,
    )

    return {
        "opened": opened,
        "fps": fps,
        "frame_count": frame_count,
        "frame_read_ok": True,
        "frame_shape": list(frame.shape),
        "frame_mean": float(np.mean(frame)),
        "frame_std": float(np.std(frame)),
        "detections_found": int(len(detections)),
        "roboflow_key_configured": bool(settings.roboflow_api_key),
    }
