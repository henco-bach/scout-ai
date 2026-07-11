# Developer Setup

## Prerequisites

- Node.js 22+
- Python 3.11+
- Docker (optional — only needed for the containerized/full-stack path)

## Frontend

```bash
cd scout-ai
npm install
npm run dev
```

Runs at http://localhost:3000. Copy `apps/frontend/.env.example` to
`apps/frontend/.env.local` if you need to point at a non-default backend
URL.

## Backend

```bash
cd scout-ai/apps/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

alembic upgrade head
uvicorn scout_ai_backend.main:app --reload --port 8000
```

Runs at http://localhost:8000, docs at http://localhost:8000/docs. No
external services required — SQLite and uploaded videos are stored under
`apps/backend/data/` by default, and `AI_PROVIDER=mock` (the default) needs
no API key.

To use a real AI provider, set `AI_PROVIDER` to `fireworks`, `gemini`, or
`openrouter` in `.env` and fill in the matching API key.

## Full stack via Docker Compose

```bash
docker compose -f docker/docker-compose.yml up --build
```

Starts the FastAPI backend and the Next.js frontend together. Uploaded
videos and the SQLite database persist in the `scout_ai_data` Docker volume.

## Tests

```bash
# Frontend
cd apps/frontend && npm run lint && npm run typecheck

# Backend
cd apps/backend && pytest
```
