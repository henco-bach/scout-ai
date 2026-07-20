# Scout AI

### Football intelligence from one smartphone recording.

[Live demo](https://scout-ai-sepia.vercel.app) · [Architecture](docs/architecture.md) · [Local setup](docs/setup.md) · [Deployment](docs/deployment.md)

Scout AI turns ordinary match footage into accessible tactical analysis for teams
that do not have an analyst or an enterprise video platform. Upload a recording
and the system detects and tracks players, clusters teams, estimates possession,
builds heatmaps, and produces a grounded tactical report.

Built for the **AMD Developer Hackathon: ACT II — Unicorn Track**.

## What it demonstrates

- An end-to-end computer-vision workflow using YOLO and ByteTrack
- Team clustering from kit colours and player-level spatial analysis
- Statistics-derived AI reports through a provider-independent interface
- A typed Next.js dashboard backed by a domain-oriented FastAPI service
- An intentionally small MVP architecture that runs without paid services or API keys

## How it works

```mermaid
flowchart LR
    A["Upload match video"] --> B["FastAPI ingestion"]
    B --> C["YOLO detection"]
    C --> D["ByteTrack tracking"]
    D --> E["Team clustering"]
    E --> F["Match statistics"]
    F --> G["Grounded AI report"]
    F --> H["Next.js dashboard"]
    G --> H
```

The language model receives only statistics computed by the vision pipeline. The
provider layer cannot invent measurements that the analysis did not produce.

## Architecture

| Layer | Technology | Responsibility |
|---|---|---|
| Web | Next.js 15, TypeScript, Tailwind, TanStack Query | Upload flow, processing status, match dashboard |
| API | FastAPI, Pydantic | Typed endpoints, dependency wiring, background orchestration |
| Vision | YOLO, ByteTrack, Supervision | Detection, tracking, clustering and spatial metrics |
| AI | Mock, Fireworks, Gemini, OpenRouter | Tactical narrative generated from computed statistics |
| Data | SQLAlchemy, SQLite, local storage | Match records, player data and uploaded video |
| Delivery | Docker Compose, GitHub Actions | Reproducible development and automated checks |

The MVP deliberately uses SQLite, local file storage, and FastAPI
`BackgroundTasks`. A database server and distributed queue would add operational
cost without improving the single-user hackathon workflow. The boundaries are
kept explicit so Postgres, object storage, and a worker queue can replace them when
usage requires it. Read the [architecture notes](docs/architecture.md) for the
trade-offs.

## Repository map

```text
apps/
  frontend/   Next.js application and match dashboard
  backend/    FastAPI service, domain model, vision pipeline and AI providers
packages/
  shared/     TypeScript domain types
docker/       Container definitions and Docker Compose
docs/         Architecture, setup, deployment and contribution guides
.github/      Continuous-integration workflows
```

## Run locally

The default mock AI provider requires no API key.

```bash
git clone https://github.com/henco-bach/scout-ai.git
cd scout-ai
npm install
npm run dev
```

Run the backend in a second terminal:

```bash
cd apps/backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn scout_ai_backend.main:app --reload --port 8000
```

For Docker and provider configuration, see the complete [setup guide](docs/setup.md).

## Validate

```bash
cd apps/frontend && npm run lint && npm run typecheck
cd apps/backend && pytest
```

## Current scope

Scout AI is a hackathon MVP, not a production analytics service. Processing runs
in-process, files are stored locally, and the pipeline is designed around a single
match workflow. The next production steps would be persistent object storage,
queued GPU workers, Postgres, authentication, evaluation datasets, and calibrated
accuracy reporting.
