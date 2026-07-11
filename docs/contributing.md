# Contributing

## Development rules (from the project brief)

- Build in milestones. Each milestone is fully completed, explained, then
  paused for approval before the next one starts.
- No placeholder code, no scaffolding left half-finished, no invented
  statistics in AI-generated reports — the AI layer only narrates numbers
  the computer-vision pipeline actually produced.
- Roadmap features are architected (folder structure, types, feature flags)
  but stay behind a flag in `apps/frontend/src/config/feature-flags.ts`
  until their milestone ships.

## Code standards

- Every component gets a typed props interface.
- `camelCase` functions, `PascalCase` components (frontend); `snake_case`
  functions, `PascalCase` classes (backend).
- Backend domain code (`domain/`) must not import FastAPI or SQLAlchemy —
  only `infrastructure/` and `api/` may depend on those.
- Don't reach for Postgres/Redis/Celery/Supabase again without a concrete
  reason — SQLite + local storage + FastAPI `BackgroundTasks` cover this
  project's needs, and previously carrying that infrastructure with a
  single-instance hackathon MVP was exactly the over-engineering this
  codebase was rebuilt to avoid.
- Every user-facing feature needs loading, error, and success states.

## Before opening a PR

```bash
# frontend
cd apps/frontend && npm run lint && npm run typecheck && npm run build

# backend
cd apps/backend && ruff check . && mypy src && pytest
```
