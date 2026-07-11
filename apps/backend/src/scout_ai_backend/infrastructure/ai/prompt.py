import json
from datetime import UTC, datetime

from scout_ai_backend.domain.entities.report import TacticalReport
from scout_ai_backend.domain.entities.statistics import MatchStatistics

SYSTEM_PROMPT = (
    "You are a professional football match analyst. You will be given match "
    "statistics computed by a computer-vision pipeline: possession estimate, "
    "average distance covered, players tracked, a passing network (which "
    "players passed to which, and how often), and a momentum timeline "
    "(possession split across windows of the match), split by Home and Away "
    "team. "
    "Write a tactical report using ONLY the numbers provided. Never invent, "
    "estimate, or introduce a statistic that was not given to you. "
    "Respond with strict JSON: "
    '{"summary": string, "insights": string[], "recommendations": string[]}. '
    "summary is 2-3 sentences. insights is 3-5 bullet-style observations. "
    "recommendations is 2-3 concrete coaching suggestions."
)


class ReportGenerationError(Exception):
    pass


def build_user_prompt(match_title: str, stats: MatchStatistics) -> str:
    lines = [
        f"Match: {match_title}",
        f"Possession estimate — Home: {stats.possession_estimate.home}%, "
        f"Away: {stats.possession_estimate.away}%",
        f"Average distance covered — Home: {stats.average_distance_covered_km.home}km, "
        f"Away: {stats.average_distance_covered_km.away}km",
        f"Players tracked: {stats.players_tracked}",
    ]

    if stats.momentum:
        momentum_str = ", ".join(
            f"{p.time_seconds}s: Home {p.home_possession_pct}%/Away {p.away_possession_pct}%"
            for p in stats.momentum
        )
        lines.append(f"Momentum over time: {momentum_str}")

    if stats.passing_network:
        top_edges = sorted(stats.passing_network, key=lambda e: e.count, reverse=True)[:10]
        edges_str = ", ".join(
            f"#{e.from_track_id}->#{e.to_track_id} ({e.count})" for e in top_edges
        )
        lines.append(f"Top passing combinations: {edges_str}")

    return "\n".join(lines) + "\n"


def parse_report(raw: str, stats: MatchStatistics, model_name: str) -> TacticalReport:
    try:
        parsed = json.loads(raw)
        summary = str(parsed["summary"])
        insights = [str(item) for item in parsed["insights"]]
        recommendations = [str(item) for item in parsed["recommendations"]]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ReportGenerationError(f"Model returned an unparsable report: {raw!r}") from exc

    return TacticalReport(
        match_id=stats.match_id,
        summary=summary,
        insights=insights,
        recommendations=recommendations,
        generated_at=datetime.now(UTC),
        model=model_name,
    )
