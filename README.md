# Scout AI

Football Intelligence for Every Team.

Upload a single smartphone recording of a football match, get back
tactical analysis: player detection and tracking (YOLO + ByteTrack), team
clustering, heatmaps, a possession estimate, and an AI-generated tactical
report — the kind of analysis Hudl/Wyscout charge thousands for, built for
clubs that can't afford that.

## Monorepo layout

```
apps/
  frontend/   Next.js 15 + TypeScript + Tailwind + shadcn/ui
  backend/    FastAPI + SQLAlchemy (SQLite) + Alembic, DDD-structured
              infrastructure/vision/  — YOLO + ByteTrack CV pipeline
              infrastructure/ai/      — AIProvider (Mock/Fireworks/Gemini/OpenRouter)
packages/
  shared/     TypeScript types shared by the frontend (mirrors backend domain entities)
docker/       Dockerfiles + docker-compose for local full-stack dev
docs/         Architecture, setup, deployment, contributing guides
.github/      CI workflows
```

No Postgres, Redis, Celery, or Supabase — SQLite, local file storage, and
FastAPI `BackgroundTasks` are enough for this single-workflow MVP. See
[docs/architecture.md](docs/architecture.md) for why.

See [docs/setup.md](docs/setup.md) to run locally — it works out of the
box with no API keys (`AI_PROVIDER=mock` by default).

## Status

Being built for the **AMD Developer Hackathon: ACT II** (Unicorn Track),
submissions close July 11, 2026. See `context/scout-ai.md` at the
workspace root for the full brief and current build plan.
