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

1. Create backend env at `/Users/joon/PycharmProjects/ai-career-concierge/.env.development` from [`/.env.example`](/Users/joon/PycharmProjects/ai-career-concierge/.env.example).
2. Create web env at [`apps/web/.env.development`](/Users/joon/PycharmProjects/ai-career-concierge/apps/web/.env.development) from [`apps/web/.env.example`](/Users/joon/PycharmProjects/ai-career-concierge/apps/web/.env.example).
3. Fill only dev credentials.
4. Keep scheduled execution disabled locally unless explicitly testing it.

Environment ownership:

- Root `.env.*` files are for FastAPI and backend services.
- `apps/web/.env.*` files are for the Next.js app.
- `NEXT_PUBLIC_*` values must live in `apps/web/.env.*`.
- Secrets must not use `NEXT_PUBLIC_*`.
- `SUPABASE_SERVICE_ROLE_KEY` is required for backend profile, dashboard, and feedback persistence.
- `DATABASE_URL` is a legacy optional value for direct Postgres tooling only, not the default PoC runtime path.

## Repository Layout

The current boilerplate keeps the backend in Python `src/*` modules and isolates the Next.js frontend in `apps/web`.

```text
apps/web          Next.js App Router frontend
src/api           FastAPI routes, schemas, dependencies, services
src/agent         LangGraph workflow, prompts, typed pipeline state
src/scraper       Source-specific scraper interfaces and normalizers
src/db            Legacy SQLModel models, repository history, and schema references
src/common        Shared config, logging, telemetry, ids, errors
tests             Unit, integration, contract, resilience coverage
```

## Local Commands

Backend:

```bash
cp .env.example .env.development
poetry install
poetry run playwright install chromium
poetry run dev
```

Frontend:

```bash
cd apps/web
cp .env.example .env.development
npm install
npm run dev
npm run test
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
- The default runtime now uses a real Gemini evaluator when `GEMINI_API_KEY` is configured; tests still inject mock or fixture evaluators explicitly.
- The default runtime now targets an Incruit scraper, while tests and local fixtures can still inject mock scrapers explicitly.
- The web app now uses Supabase SSR sessions for Google OAuth and forwards real Supabase bearer tokens to FastAPI.
- FastAPI verifies Supabase JWTs against the project JWKS before resolving `UserIdentity`.
- Production-facing secrets are validated through typed settings in `src/common/config.py`.
- Supabase OAuth redirect URLs must allow the web callback path `/auth/callback`.
- Backend persistence now uses the Supabase Data API with `SUPABASE_SERVICE_ROLE_KEY` for both user-facing flows and the pipeline runtime.
- Schema changes are managed through Supabase SQL/MCP rather than Alembic as the default PoC workflow.
- Local API entry points:
  - `/` returns a lightweight welcome payload
  - `/healthz` returns runtime health info
  - `/docs` opens Swagger UI

## Scraper Notes

- The scraper runtime is configured from root backend env files.
- `SCRAPER_MAX_PAGES` limits pagination during development so local runs stay safe.
- `SCRAPER_HEADLESS=true` is the recommended default for local and CI runs.
- Live scraping is not part of the automated test suite; scraper tests use HTML fixtures and injected fetchers.

## Login QA Checklist

- Open `/login` and confirm the login copy and button render correctly.
- Click `Continue with Google` and confirm the browser moves to the Google sign-in page.
- Open a protected route such as `/dashboard`, verify it redirects to `/login?next=/dashboard`, then confirm login returns to `/dashboard`.
- Use an account with an empty onboarding profile and confirm direct login lands on `/dashboard` with an onboarding prompt.
