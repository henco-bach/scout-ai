from pathlib import Path
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile

from scout_ai_backend.api.deps import get_match_service, get_video_storage
from scout_ai_backend.domain.entities.match import Match
from scout_ai_backend.domain.services.match_processor import process_match
from scout_ai_backend.domain.services.match_service import MatchService
from scout_ai_backend.infrastructure.storage.local_storage import LocalVideoStorage
from scout_ai_backend.schemas.match import (
    MatchDetailResponse,
    MatchResponse,
    MatchStatisticsResponse,
    PlayerResponse,
    PositionSchema,
    TacticalReportResponse,
)


class RenamePlayerRequest(BaseModel):
    name: str | None

router = APIRouter(tags=["matches"])


def _annotated_video_url(match: Match) -> str | None:
    if match.annotated_video_path is None:
        return None
    return f"/media/{Path(match.annotated_video_path).name}"


def _to_match_response(match: Match) -> MatchResponse:
    return MatchResponse(
        id=match.id,
        title=match.title,
        stage=match.stage,
        error_message=match.error_message,
        video_url=f"/media/{Path(match.video_path).name}",
        annotated_video_url=_annotated_video_url(match),
        kickoff_offset_seconds=match.kickoff_offset_seconds,
        created_at=match.created_at,
        updated_at=match.updated_at,
    )


@router.post("/matches", response_model=MatchResponse, status_code=201)
async def upload_match(
    background_tasks: BackgroundTasks,
    service: Annotated[MatchService, Depends(get_match_service)],
    storage: Annotated[LocalVideoStorage, Depends(get_video_storage)],
    title: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    kickoff_offset_seconds: Annotated[float, Form()] = 0.0,
) -> MatchResponse:
    content = await file.read()
    video_path = await storage.save(file.filename or "match.mp4", content)
    match = await service.create_match(
        title=title, video_path=video_path, kickoff_offset_seconds=kickoff_offset_seconds
    )
    background_tasks.add_task(process_match, match.id)
    return _to_match_response(match)


@router.get("/matches", response_model=list[MatchResponse])
async def list_matches(
    service: Annotated[MatchService, Depends(get_match_service)],
) -> list[MatchResponse]:
    matches = await service.list_matches()
    return [_to_match_response(match) for match in matches]


@router.get("/matches/{match_id}", response_model=MatchDetailResponse)
async def get_match(
    match_id: UUID,
    service: Annotated[MatchService, Depends(get_match_service)],
) -> MatchDetailResponse:
    match = await service.get_match(match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    players = await service.get_players(match_id)

    return MatchDetailResponse(
        id=match.id,
        title=match.title,
        stage=match.stage,
        error_message=match.error_message,
        video_url=f"/media/{Path(match.video_path).name}",
        annotated_video_url=_annotated_video_url(match),
        kickoff_offset_seconds=match.kickoff_offset_seconds,
        created_at=match.created_at,
        updated_at=match.updated_at,
        statistics=(
            MatchStatisticsResponse.model_validate(match.statistics) if match.statistics else None
        ),
        report=(TacticalReportResponse.model_validate(match.report) if match.report else None),
        players=[
            PlayerResponse(
                id=player.id,
                team=player.team.value,
                track_id=player.track_id,
                name=player.name,
                average_position=PositionSchema(
                    x=player.average_position.x, y=player.average_position.y
                ),
                distance_covered_km=player.distance_covered_km,
                touches=player.touches,
                passes_made=player.passes_made,
                passes_received=player.passes_received,
                rating=player.rating,
                heatmap=player.heatmap,
            )
            for player in players
        ],
    )


@router.delete("/matches/{match_id}", status_code=204)
async def delete_match(
    match_id: UUID,
    service: Annotated[MatchService, Depends(get_match_service)],
) -> None:
    match = await service.get_match(match_id)
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    for video_path in (match.video_path, match.annotated_video_path):
        if video_path:
            Path(video_path).unlink(missing_ok=True)

    await service.delete_match(match_id)


@router.patch("/players/{player_id}", response_model=PlayerResponse)
async def rename_player(
    player_id: UUID,
    body: RenamePlayerRequest,
    service: Annotated[MatchService, Depends(get_match_service)],
) -> PlayerResponse:
    player = await service.rename_player(player_id, body.name)
    return PlayerResponse(
        id=player.id,
        team=player.team.value,
        track_id=player.track_id,
        name=player.name,
        average_position=PositionSchema(x=player.average_position.x, y=player.average_position.y),
        distance_covered_km=player.distance_covered_km,
        touches=player.touches,
        passes_made=player.passes_made,
        passes_received=player.passes_received,
        rating=player.rating,
        heatmap=player.heatmap,
    )
