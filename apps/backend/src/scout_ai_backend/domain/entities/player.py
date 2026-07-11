from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class TeamSide(StrEnum):
    HOME = "home"
    AWAY = "away"


@dataclass(slots=True)
class Position:
    x: float
    y: float


@dataclass(slots=True)
class Player:
    id: UUID
    match_id: UUID
    team: TeamSide
    track_id: str
    average_position: Position
    distance_covered_km: float
    heatmap: list[list[float]]
    touches: int
    passes_made: int
    passes_received: int
    rating: float
    name: str | None = None
