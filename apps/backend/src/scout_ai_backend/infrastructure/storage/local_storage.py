import uuid
from pathlib import Path

from scout_ai_backend.core.config import Settings


class LocalVideoStorage:
    """Saves uploaded match videos to the local filesystem."""

    def __init__(self, settings: Settings) -> None:
        self._storage_dir = Path(settings.storage_dir)
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    async def save(self, filename: str, content: bytes) -> str:
        suffix = Path(filename).suffix or ".mp4"
        path = self._storage_dir / f"{uuid.uuid4()}{suffix}"
        path.write_bytes(content)
        return str(path)
