from datetime import datetime

from sqlalchemy import JSON, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from scout_ai_backend.infrastructure.database.session import Base


class MatchModel(Base):
    __tablename__ = "matches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    video_path: Mapped[str] = mapped_column(String(1024))
    annotated_video_path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    kickoff_offset_seconds: Mapped[float] = mapped_column(default=0.0)
    stage: Mapped[str] = mapped_column(String(32))
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    statistics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    report: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

    players: Mapped[list["PlayerModel"]] = relationship(
        back_populates="match", cascade="all, delete-orphan"
    )


class PlayerModel(Base):
    __tablename__ = "players"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    match_id: Mapped[str] = mapped_column(String(36), ForeignKey("matches.id"), index=True)
    team: Mapped[str] = mapped_column(String(8))
    track_id: Mapped[str] = mapped_column(String(64))
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    average_position_x: Mapped[float]
    average_position_y: Mapped[float]
    distance_covered_km: Mapped[float]
    heatmap: Mapped[list] = mapped_column(JSON)
    touches: Mapped[int]
    passes_made: Mapped[int]
    passes_received: Mapped[int]
    rating: Mapped[float]

    match: Mapped["MatchModel"] = relationship(back_populates="players")
