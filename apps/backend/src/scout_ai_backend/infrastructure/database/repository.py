from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from scout_ai_backend.domain.entities.match import Match, ProcessingStage
from scout_ai_backend.domain.entities.player import Player, Position, TeamSide
from scout_ai_backend.infrastructure.database.models import MatchModel, PlayerModel


def _match_to_entity(model: MatchModel) -> Match:
    return Match(
        id=UUID(model.id),
        title=model.title,
        video_path=model.video_path,
        annotated_video_path=model.annotated_video_path,
        kickoff_offset_seconds=model.kickoff_offset_seconds,
        stage=ProcessingStage(model.stage),
        created_at=model.created_at,
        updated_at=model.updated_at,
        error_message=model.error_message,
        statistics=model.statistics,
        report=model.report,
    )


def _player_to_entity(model: PlayerModel) -> Player:
    return Player(
        id=UUID(model.id),
        match_id=UUID(model.match_id),
        team=TeamSide(model.team),
        track_id=model.track_id,
        name=model.name,
        average_position=Position(x=model.average_position_x, y=model.average_position_y),
        distance_covered_km=model.distance_covered_km,
        heatmap=model.heatmap,
        touches=model.touches,
        passes_made=model.passes_made,
        passes_received=model.passes_received,
        rating=model.rating,
    )


@dataclass(slots=True)
class MatchRepository:
    """Single concrete data-access layer for matches and players (SQLite)."""

    session: AsyncSession

    async def get(self, match_id: UUID) -> Match | None:
        model = await self.session.get(MatchModel, str(match_id))
        return _match_to_entity(model) if model else None

    async def list_all(self) -> list[Match]:
        result = await self.session.execute(
            select(MatchModel).order_by(MatchModel.created_at.desc())
        )
        return [_match_to_entity(model) for model in result.scalars().all()]

    async def create(self, match: Match) -> Match:
        model = MatchModel(
            id=str(match.id),
            title=match.title,
            video_path=match.video_path,
            kickoff_offset_seconds=match.kickoff_offset_seconds,
            stage=match.stage.value,
            error_message=match.error_message,
            created_at=match.created_at,
            updated_at=match.updated_at,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return _match_to_entity(model)

    async def update_stage(
        self,
        match_id: UUID,
        stage: ProcessingStage,
        *,
        error_message: str | None = None,
    ) -> None:
        model = await self.session.get(MatchModel, str(match_id))
        if model is None:
            raise ValueError(f"Match {match_id} not found")
        model.stage = stage.value
        model.error_message = error_message
        await self.session.commit()

    async def save_results(
        self,
        match_id: UUID,
        *,
        statistics: dict,
        players: list[Player],
        report: dict,
        annotated_video_path: str | None = None,
    ) -> None:
        model = await self.session.get(MatchModel, str(match_id))
        if model is None:
            raise ValueError(f"Match {match_id} not found")
        model.annotated_video_path = annotated_video_path
        model.statistics = statistics
        model.report = report
        model.stage = ProcessingStage.COMPLETED.value
        for player in players:
            self.session.add(
                PlayerModel(
                    id=str(player.id),
                    match_id=str(match_id),
                    team=player.team.value,
                    track_id=player.track_id,
                    name=player.name,
                    average_position_x=player.average_position.x,
                    average_position_y=player.average_position.y,
                    distance_covered_km=player.distance_covered_km,
                    heatmap=player.heatmap,
                    touches=player.touches,
                    passes_made=player.passes_made,
                    passes_received=player.passes_received,
                    rating=player.rating,
                )
            )
        await self.session.commit()

    async def get_players(self, match_id: UUID) -> list[Player]:
        result = await self.session.execute(
            select(PlayerModel).where(PlayerModel.match_id == str(match_id))
        )
        return [_player_to_entity(model) for model in result.scalars().all()]

    async def rename_player(self, player_id: UUID, name: str | None) -> Player:
        model = await self.session.get(PlayerModel, str(player_id))
        if model is None:
            raise ValueError(f"Player {player_id} not found")
        model.name = name
        await self.session.commit()
        await self.session.refresh(model)
        return _player_to_entity(model)

    async def delete(self, match_id: UUID) -> bool:
        model = await self.session.get(MatchModel, str(match_id))
        if model is None:
            return False
        await self.session.delete(model)
        await self.session.commit()
        return True
