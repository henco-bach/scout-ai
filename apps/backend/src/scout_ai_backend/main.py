from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from scout_ai_backend.api.v1.router import api_router
from scout_ai_backend.core.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    # No cookies/auth are ever sent by the frontend, so credentials aren't
    # needed — and Starlette refuses to emit Access-Control-Allow-Origin at
    # all when allow_origins=["*"] is combined with allow_credentials=True
    # (invalid per the CORS spec), silently breaking every request.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_v1_prefix)

storage_path = Path(settings.storage_dir)
storage_path.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=storage_path), name="media")
