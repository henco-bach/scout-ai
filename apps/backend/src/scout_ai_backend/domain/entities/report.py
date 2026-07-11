from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class TacticalReport:
    """Narrates statistics the CV pipeline produced. Never invents numbers."""

    match_id: UUID
    summary: str
    insights: list[str]
    recommendations: list[str]
    generated_at: datetime
    model: str
