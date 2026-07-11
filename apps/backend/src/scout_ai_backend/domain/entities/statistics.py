from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class TeamSplit:
    home: float
    away: float


@dataclass(slots=True)
class PassEdge:
    """A pass between two same-team players, inferred from consecutive
    changes in which player was nearest the ball."""

    from_track_id: str
    to_track_id: str
    count: int


@dataclass(slots=True)
class MomentumPoint:
    """Possession split within one time window of the match."""

    time_seconds: float
    home_possession_pct: float
    away_possession_pct: float


@dataclass(slots=True)
class PassTimelinePoint:
    """Number of passes completed within one time window of the match."""

    time_seconds: float
    count: int


@dataclass(slots=True)
class MatchStatistics:
    """Output of the computer-vision pipeline. The only source of truth
    the AI report generator is allowed to narrate — nothing else."""

    match_id: UUID
    possession_estimate: TeamSplit
    average_distance_covered_km: TeamSplit
    players_tracked: int
    passing_network: list[PassEdge]
    momentum: list[MomentumPoint]
    pass_timeline: list[PassTimelinePoint]
    passes_by_team: TeamSplit
    pass_accuracy: TeamSplit
