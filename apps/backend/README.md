# Scout AI Backend

FastAPI service for match ingestion, computer-vision orchestration, and AI tactical reports.

## Layout

```
src/scout_ai_backend/
├── api/            # FastAPI routers, request/response wiring, DI
├── core/           # settings, cross-cutting config
├── domain/         # entities, repository interfaces (ports), services (use cases)
├── infrastructure/ # SQLAlchemy models + repository implementations, Celery, storage
└── schemas/        # Pydantic request/response models
```

Domain code depends only on abstractions (`domain/repositories`), never on
SQLAlchemy or FastAPI directly — infrastructure implements those ports. This
keeps the CV/AI pipelines and persistence layer swappable.

## Local setup

Requires Python 3.11+.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env

uvicorn scout_ai_backend.main:app --reload --port 8000
```

## Migrations

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Tests

```bash
pytest
```
