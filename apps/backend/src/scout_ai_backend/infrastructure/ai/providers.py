from abc import ABC, abstractmethod
from datetime import UTC, datetime

import httpx

from scout_ai_backend.core.config import Settings
from scout_ai_backend.domain.entities.report import TacticalReport
from scout_ai_backend.domain.entities.statistics import MatchStatistics
from scout_ai_backend.infrastructure.ai.prompt import SYSTEM_PROMPT, build_user_prompt, parse_report


class AIProvider(ABC):
    """Turns computer-vision statistics into a tactical report. Implementations
    must never introduce a number that wasn't in the given statistics."""

    @abstractmethod
    async def generate_report(self, match_title: str, stats: MatchStatistics) -> TacticalReport: ...


class MockProvider(AIProvider):
    """Deterministic, template-based report. No network calls, no API key —
    this is the default so the app works out of the box."""

    async def generate_report(self, match_title: str, stats: MatchStatistics) -> TacticalReport:
        home, away = stats.possession_estimate.home, stats.possession_estimate.away
        leader = "Home" if home >= away else "Away"
        dist_home = stats.average_distance_covered_km.home
        dist_away = stats.average_distance_covered_km.away

        summary = (
            f"{match_title}: {leader} controlled more of the ball "
            f"({home:.0f}% - {away:.0f}%), with {stats.players_tracked} players "
            f"tracked across the match."
        )
        insights = [
            f"Home averaged {dist_home:.1f}km covered per player, Away averaged {dist_away:.1f}km.",
            f"Possession split: Home {home:.0f}% / Away {away:.0f}%.",
            f"{stats.players_tracked} players were detected and tracked throughout the match.",
        ]
        if stats.passing_network:
            top_edge = max(stats.passing_network, key=lambda e: e.count)
            insights.append(
                f"Most frequent passing combination: #{top_edge.from_track_id} to "
                f"#{top_edge.to_track_id} ({top_edge.count} times)."
            )
        recommendations = [
            "Review pressing triggers for the team with less possession.",
            "Compare individual player distance covered against the team average to spot fatigue.",
        ]

        return TacticalReport(
            match_id=stats.match_id,
            summary=summary,
            insights=insights,
            recommendations=recommendations,
            generated_at=datetime.now(UTC),
            model="mock",
        )


class OpenAICompatibleProvider(AIProvider):
    """Shared implementation for any OpenAI chat-completions-compatible API
    (Fireworks AI, OpenRouter)."""

    def __init__(self, *, base_url: str, api_key: str, model: str) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._model = model

    async def generate_report(self, match_title: str, stats: MatchStatistics) -> TacticalReport:
        user_prompt = build_user_prompt(match_title, stats)
        async with httpx.AsyncClient(base_url=self._base_url, timeout=60.0) as client:
            response = await client.post(
                "/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "model": self._model,
                    "temperature": 0.3,
                    "max_tokens": 800,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                },
            )
            response.raise_for_status()
            raw: str = response.json()["choices"][0]["message"]["content"]
        return parse_report(raw, stats, self._model)


class GeminiProvider(AIProvider):
    """Google Gemini via the Generative Language API."""

    _BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, *, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    async def generate_report(self, match_title: str, stats: MatchStatistics) -> TacticalReport:
        user_prompt = build_user_prompt(match_title, stats)
        async with httpx.AsyncClient(base_url=self._BASE_URL, timeout=60.0) as client:
            response = await client.post(
                f"/models/{self._model}:generateContent",
                params={"key": self._api_key},
                json={
                    "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                    "contents": [{"parts": [{"text": user_prompt}]}],
                    "generationConfig": {"temperature": 0.3, "maxOutputTokens": 800},
                },
            )
            response.raise_for_status()
            payload = response.json()
            raw: str = payload["candidates"][0]["content"]["parts"][0]["text"]
        return parse_report(raw, stats, self._model)


def get_ai_provider(settings: Settings) -> AIProvider:
    if settings.ai_provider == "fireworks":
        return OpenAICompatibleProvider(
            base_url="https://api.fireworks.ai/inference/v1",
            api_key=settings.fireworks_api_key,
            model=settings.fireworks_model,
        )
    if settings.ai_provider == "gemini":
        return GeminiProvider(api_key=settings.gemini_api_key, model=settings.gemini_model)
    if settings.ai_provider == "openrouter":
        return OpenAICompatibleProvider(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
            model=settings.openrouter_model,
        )
    return MockProvider()
