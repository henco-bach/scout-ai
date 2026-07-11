# Deployment

## Frontend — Vercel

- Root directory: `apps/frontend`
- Build command: `npm run build --workspace=frontend` (run from repo root so
  the `@scout-ai/shared` workspace package resolves)
- Environment: `NEXT_PUBLIC_API_URL`

## Backend — AMD Developer Cloud / Railway

Single service, `docker/backend.Dockerfile` (FastAPI, port 8000). No
separate worker or broker — background processing runs in-process via
FastAPI `BackgroundTasks`.

- SQLite database and uploaded videos live under `/app/data` inside the
  container — mount a persistent volume there, or accept ephemeral storage
  for a demo deployment.
- Environment: see `apps/backend/.env.example`. Set `AI_PROVIDER` to
  `fireworks`, `gemini`, or `openrouter` with the matching API key once
  credentials are available; otherwise it defaults to `mock`.
- For the AMD Developer Cloud specifically: the CV pipeline (YOLO via
  `ultralytics`, PyTorch) runs on CPU by default. To use AMD Instinct GPUs,
  install ROCm-enabled PyTorch in the image (swap the `pip install` index
  URL) rather than the default CPU wheel.

## Migrations

Baked into the container start command (`alembic upgrade head` runs before
`uvicorn` starts — see `docker/backend.Dockerfile`).

## CI

`.github/workflows/ci.yml` runs on every push/PR:

- Frontend: install, lint, typecheck, build
- Backend: install, ruff, mypy, pytest

Deployment itself is not wired into CI yet.
