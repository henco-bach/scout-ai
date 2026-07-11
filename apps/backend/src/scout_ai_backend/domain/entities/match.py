from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class ProcessingStage(StrEnum):
    UPLOADED = "uploaded"
    ANALYZING_VIDEO = "analyzing_video"  # detection + tracking + stats
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(slots=True)
class Match:
    id: UUID
    title: str
    video_path: str
    stage: ProcessingStage
    created_at: datetime
    updated_at: datetime
    error_message: str | None = None
    annotated_video_path: str | None = None
    kickoff_offset_seconds: float = 0.0
    # Raw JSON blobs (validated at the API boundary via Pydantic schemas) —
    # populated once the pipeline reaches GENERATING_REPORT/COMPLETED.
    statistics: dict | None = None
    report: dict | None = None
