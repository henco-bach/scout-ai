from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from scout_ai_backend.core.config import Settings, get_settings
from scout_ai_backend.domain.services.match_service import MatchService
from scout_ai_backend.infrastructure.database.repository import MatchRepository
from scout_ai_backend.infrastructure.database.session import get_db_session
from scout_ai_backend.infrastructure.storage.local_storage import LocalVideoStorage

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_match_repository(session: DbSession) -> MatchRepository:
    return MatchRepository(session=session)


def get_match_service(
    repository: Annotated[MatchRepository, Depends(get_match_repository)],
) -> MatchService:
    return MatchService(repository=repository)


def get_video_storage(settings: SettingsDep) -> LocalVideoStorage:
    return LocalVideoStorage(settings)
