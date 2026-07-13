import uuid
from datetime import UTC, datetime

from scout_ai_backend.domain.entities.match import Match, ProcessingStage
from scout_ai_backend.domain.entities.player import Player
from scout_ai_backend.infrastructure.database.repository import MatchRepository


class MatchService:
    def __init__(self, repository: MatchRepository) -> None:
        self._repository = repository

    async def create_match(
        self, title: str, video_path: str, kickoff_offset_seconds: float = 0.0
    ) -> Match:
        now = datetime.now(UTC)
        match = Match(
            id=uuid.uuid4(),
            title=title,
            video_path=video_path,
            kickoff_offset_seconds=kickoff_offset_seconds,
            stage=ProcessingStage.UPLOADED,
            created_at=now,
            updated_at=now,
        )
        return await self._repository.create(match)

    async def rename_player(self, player_id: uuid.UUID, name: str | None) -> Player:
        return await self._repository.rename_player(player_id, name)

    async def get_match(self, match_id: uuid.UUID) -> Match | None:
        return await self._repository.get(match_id)

    async def list_matches(self) -> list[Match]:
        return await self._repository.list_all()

    async def get_players(self, match_id: uuid.UUID) -> list[Player]:
        return await self._repository.get_players(match_id)

    async def delete_match(self, match_id: uuid.UUID) -> bool:
        return await self._repository.delete(match_id)
