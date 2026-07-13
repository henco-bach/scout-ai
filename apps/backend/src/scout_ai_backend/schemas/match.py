from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from scout_ai_backend.domain.entities.match import ProcessingStage


class TeamSplitSchema(BaseModel):
    home: float
    away: float


class PassEdgeSchema(BaseModel):
    from_track_id: str
    to_track_id: str
    count: int


class MomentumPointSchema(BaseModel):
    time_seconds: float
    home_possession_pct: float
    away_possession_pct: float


class PassTimelinePointSchema(BaseModel):
    time_seconds: float
    count: int


class MatchStatisticsResponse(BaseModel):
    possession_estimate: TeamSplitSchema
    average_distance_covered_km: TeamSplitSchema
    players_tracked: int
    passing_network: list[PassEdgeSchema]
    momentum: list[MomentumPointSchema]
    # Older stored matches were processed before these fields existed.
    pass_timeline: list[PassTimelinePointSchema] = Field(default_factory=list)
    passes_by_team: TeamSplitSchema = Field(default_factory=lambda: TeamSplitSchema(home=0, away=0))
    pass_accuracy: TeamSplitSchema = Field(default_factory=lambda: TeamSplitSchema(home=0, away=0))


class TacticalReportResponse(BaseModel):
    summary: str
    insights: list[str]
    recommendations: list[str]
    generated_at: datetime
    model: str


class PositionSchema(BaseModel):
    x: float
    y: float


class PlayerResponse(BaseModel):
    id: UUID
    team: str
    track_id: str
    name: str | None = None
    average_position: PositionSchema
    distance_covered_km: float
    heatmap: list[list[float]]
    touches: int
    passes_made: int
    passes_received: int
    rating: float


class MatchResponse(BaseModel):
    id: UUID
    title: str
    stage: ProcessingStage
    error_message: str | None
    video_url: str
    annotated_video_url: str | None
    kickoff_offset_seconds: float = 0.0
    created_at: datetime
    updated_at: datetime


class MatchDetailResponse(MatchResponse):
    statistics: MatchStatisticsResponse | None
    report: TacticalReportResponse | None
    players: list[PlayerResponse]
