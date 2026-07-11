# Scout AI Architecture

## System overview

```
                     ┌─────────────────┐
                     │   Next.js 15     │  apps/frontend
                     │  (App Router)    │  Upload UI, match results dashboard
                     └────────┬─────────┘
                              │ REST (JSON) + video upload
                              ▼
                     ┌─────────────────┐
                     │    FastAPI       │  apps/backend
                     │  (async, DDD)    │  Upload endpoint, match status/detail
                     └────────┬─────────┘
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
             ┌────────────┐      ┌───────────────┐
             │   SQLite    │      │ Local storage  │
             │ (matches,   │      │ (uploaded      │
             │  players)   │      │  video files)  │
             └────────────┘      └───────────────┘
                              │
                    FastAPI BackgroundTasks
                    (no separate worker/broker)
                              │
              ┌───────────────┼────────────────┐
              ▼                                ▼
     ┌──────────────────┐           ┌────────────────────┐
     │ infrastructure/    │           │ infrastructure/ai/  │
     │ vision/pipeline.py │           │ providers.py        │
     │ YOLO + ByteTrack   │           │ Mock / Fireworks /  │
     │ (supervision)      │           │ Gemini / OpenRouter │
     └──────────────────┘           └────────────────────┘
```

Deliberately no Postgres, Redis, Celery, or Supabase — this is a
single-workflow hackathon MVP (upload → detect/track → stats → AI report),
and none of that infrastructure was pulling its weight yet. SQLite plus an
in-process `BackgroundTasks` call gives the same "process after upload"
behavior without a broker, worker process, or second Docker image to build,
deploy, and keep healthy. If Scout AI grows into a multi-user product later,
Postgres + a real task queue are the first things to bring back — this
doc's job is to make that swap easy, not to justify carrying the
infrastructure it needs.

## Backend: Domain-Driven Design

`apps/backend/src/scout_ai_backend` is split so business rules never depend on
frameworks:

- `domain/entities` — plain dataclasses (`Match`, `Player`,
  `MatchStatistics`, `TacticalReport`). No SQLAlchemy, no Pydantic.
- `domain/services` — `MatchService` (CRUD use cases) and
  `match_processor.process_match` (the background pipeline orchestration:
  CV analysis → AI report → persist).
- `infrastructure/database` — `MatchRepository` (concrete, SQLite-backed —
  see "No repository interface" below) and SQLAlchemy models.
- `infrastructure/vision` — `analyze_video_sync`: YOLO detection, ByteTrack
  tracking (via `supervision`), team clustering by shirt color, possession
  estimate, heatmaps, and distance covered. Synchronous/CPU-bound; called
  via `asyncio.to_thread` so it doesn't block the event loop.
- `infrastructure/ai` — the `AIProvider` interface and its four
  implementations (see below).
- `infrastructure/storage` — `LocalVideoStorage`, saves uploads to disk.
- `api` — FastAPI routers, Pydantic schemas, dependency injection wiring
  (`api/deps.py`).

### No repository interface

There's no `MatchRepository` abstract base class. One repository, one
implementation (SQLite) — an interface with a single implementer that never
gets swapped is exactly the premature abstraction this rebuild was cutting.
If a second backing store shows up, that's when the interface earns its
keep.

### AIProvider abstraction

`infrastructure/ai/providers.py` defines `AIProvider` (one method:
`generate_report(match_title, stats) -> TacticalReport`) with four
implementations:

- `MockProvider` — deterministic, template-based report built directly
  from the real computed statistics. No network call, no API key. This is
  the default (`AI_PROVIDER=mock`), so the app runs out of the box.
- `OpenAICompatibleProvider` — shared implementation for any
  OpenAI-chat-completions-shaped API; used for both `FireworksProvider`
  (Gemma via Fireworks AI) and `OpenRouterProvider`.
- `GeminiProvider` — Google's Generative Language API (different request/
  response shape, so it isn't a subclass of the OpenAI-compatible one).

All four build the prompt from `infrastructure/ai/prompt.py`'s
`build_user_prompt`, which only ever inserts numbers that came from the CV
pipeline — there's no code path for a provider to introduce a statistic
that wasn't computed.

## Frontend

Next.js App Router, feature-oriented under `src/`:

- `app/` — routes only (Server Components by default).
- `components/` — shared UI (`components/ui` is shadcn-generated, do not
  hand-edit primitives — compose them instead).
- `lib/api` — typed fetch client against the FastAPI backend.
- `lib/query` — TanStack Query client configuration (used to poll match
  status while the pipeline runs).
- `config/feature-flags.ts` — single source of truth for roadmap features
  that are architected but not yet shipped.

## Shared types

`packages/shared` holds TypeScript types mirrored by hand from the Python
dataclasses in `domain/entities`. No codegen bridging them yet — keeping
the mirror by hand is intentional at this stage.
