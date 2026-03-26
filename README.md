# AI Career Concierge

AI Career Concierge is a PoC job-matching system that ingests job postings, filters them through a rule-based and LLM-assisted evaluation pipeline, and delivers high-fit results through Slack.

## Docs

Read project guidance in this order:

1. [`docs/CONTEXT.md`](docs/CONTEXT.md)
2. [`docs/TRD.md`](docs/TRD.md)
3. [`docs/PRD.md`](docs/PRD.md)
4. [`AGENTS.md`](AGENTS.md)

## Environment Setup

This project separates development and production from the start.

- Development should use dev-only Supabase, Slack, OAuth, and API credentials.
- Production should use separate live credentials and scheduled delivery.
- Do not point local development at production resources by default.

Recommended local setup:

1. Create `.env.development` from `.env.example`.
2. Fill only dev credentials.
3. Keep scheduled execution disabled locally unless explicitly testing it.

## Repository Layout

The current boilerplate keeps the backend in Python `src/*` modules and isolates the Next.js frontend in `apps/web`.

```text
apps/web          Next.js App Router frontend
src/api           FastAPI routes, schemas, dependencies, services
src/agent         LangGraph workflow, prompts, typed pipeline state
src/scraper       Source-specific scraper interfaces and normalizers
src/db            SQLModel models, repositories, sessions, Alembic migrations
src/common        Shared config, logging, telemetry, ids, errors
tests             Unit, integration, contract, resilience coverage
```

## Local Commands

Backend:

```bash
poetry install
PYTHONPATH=src poetry run uvicorn api.main:app --reload
```

Frontend:

```bash
cd apps/web
npm install
npm run dev
```

Database migration:

```bash
PYTHONPATH=src poetry run alembic upgrade head
```

## Current Scope

The current goal is a single-user PoC that supports:

- login and onboarding
- job ingestion
- rule-based filtering
- LLM evaluation
- Slack delivery
- user feedback and short-term memory reuse

## Scaffold Notes

- The backend ships with a mock scraper, mock LLM evaluator, and logging Slack notifier so the end-to-end loop is runnable before real integrations are wired.
- Dev and test authentication use a scaffold bearer token (`Authorization: Bearer dev-token`) until Supabase JWT verification is connected.
- Production-facing secrets are validated through typed settings in `src/common/config.py`.
