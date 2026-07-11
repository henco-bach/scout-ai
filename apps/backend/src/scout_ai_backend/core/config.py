from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

AIProviderName = Literal["mock", "fireworks", "gemini", "openrouter"]


class Settings(BaseSettings):
    """Application configuration, sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Scout AI Backend"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    cors_origins: list[str] = ["http://localhost:3000"]

    database_url: str = "sqlite+aiosqlite:///./data/scout-ai.db"
    storage_dir: str = "./data/uploads"

    # AI report generation. "mock" needs no API key and is the default so the
    # app works out of the box; swap providers via AI_PROVIDER.
    ai_provider: AIProviderName = "mock"

    fireworks_api_key: str = ""
    # Gemma 4 26B A4B IT: Google DeepMind MoE, 256K context, hosted on Fireworks AI.
    fireworks_model: str = "accounts/fireworks/models/gemma-4-26b-a4b-it"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    openrouter_api_key: str = ""
    openrouter_model: str = "google/gemma-3-27b-it"

    # Football-specific ball/player/goalkeeper/referee detection. Empty by
    # default so the CV pipeline falls back to local YOLOv8n (no key
    # required, works out of the box) — set this to get much better ball
    # detection via Roboflow's hosted "football-players-detection" model.
    roboflow_api_key: str = ""
    roboflow_model_id: str = "football-players-detection-3zvbc/12"


@lru_cache
def get_settings() -> Settings:
    return Settings()
