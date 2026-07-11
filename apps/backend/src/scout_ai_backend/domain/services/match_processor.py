import asyncio
import uuid

from scout_ai_backend.core.config import get_settings
from scout_ai_backend.domain.entities.match import ProcessingStage
from scout_ai_backend.domain.entities.report import TacticalReport
from scout_ai_backend.domain.entities.statistics import MatchStatistics
from scout_ai_backend.infrastructure.ai.providers import get_ai_provider
from scout_ai_backend.infrastructure.database.repository import MatchRepository
from scout_ai_backend.infrastructure.database.session import async_session_factory
from scout_ai_backend.infrastructure.vision.pipeline import analyze_video_sync


def _stats_to_dict(stats: MatchStatistics) -> dict:
    return {
        "possession_estimate": {
            "home": stats.possession_estimate.home,
            "away": stats.possession_estimate.away,
        },
        "average_distance_covered_km": {
            "home": stats.average_distance_covered_km.home,
            "away": stats.average_distance_covered_km.away,
        },
        "players_tracked": stats.players_tracked,
        "passing_network": [
            {"from_track_id": edge.from_track_id, "to_track_id": edge.to_track_id, "count": edge.count}
            for edge in stats.passing_network
        ],
        "momentum": [
            {
                "time_seconds": point.time_seconds,
                "home_possession_pct": point.home_possession_pct,
                "away_possession_pct": point.away_possession_pct,
            }
            for point in stats.momentum
        ],
        "pass_timeline": [
            {"time_seconds": point.time_seconds, "count": point.count}
            for point in stats.pass_timeline
        ],
        "passes_by_team": {"home": stats.passes_by_team.home, "away": stats.passes_by_team.away},
        "pass_accuracy": {"home": stats.pass_accuracy.home, "away": stats.pass_accuracy.away},
    }


def _report_to_dict(report: TacticalReport) -> dict:
    return {
        "summary": report.summary,
        "insights": report.insights,
        "recommendations": report.recommendations,
        "generated_at": report.generated_at.isoformat(),
        "model": report.model,
    }


async def process_match(match_id: uuid.UUID) -> None:
    """Runs CV analysis -> AI report -> persist results. Executed as a
    FastAPI background task, so it owns its own DB session rather than
    reusing the request-scoped one — it outlives the HTTP request that
    triggered it."""
    settings = get_settings()

    async with async_session_factory() as session:
        repository = MatchRepository(session=session)
        match = await repository.get(match_id)
        if match is None:
            return

        try:
            await repository.update_stage(match_id, ProcessingStage.ANALYZING_VIDEO)
            stats, players, annotated_video_path = await asyncio.to_thread(
                analyze_video_sync,
                match.video_path,
                match_id,
                kickoff_offset_seconds=match.kickoff_offset_seconds,
                roboflow_api_key=settings.roboflow_api_key,
                roboflow_model_id=settings.roboflow_model_id,
            )

            await repository.update_stage(match_id, ProcessingStage.GENERATING_REPORT)
            provider = get_ai_provider(settings)
            report = await provider.generate_report(match.title, stats)

            await repository.save_results(
                match_id,
                statistics=_stats_to_dict(stats),
                players=players,
                report=_report_to_dict(report),
                annotated_video_path=annotated_video_path,
            )
        except Exception as exc:  # pipeline errors must surface on the match, not crash the app
            # A failure during a flush/commit leaves the session in a state
            # that raises on any further use until it's rolled back — without
            # this, the update_stage call below silently fails too, and the
            # match is left stuck instead of marked failed.
            await session.rollback()
            await repository.update_stage(
                match_id, ProcessingStage.FAILED, error_message=str(exc)
            )
