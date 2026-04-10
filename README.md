# AI Career Concierge

AI Career Concierge is a PoC job-matching system that ingests job postings, filters them through a rule-based and LLM-assisted evaluation pipeline, and delivers high-fit results through Slack.

## Start Here

Read project guidance in this order:

1. [`AGENTS.md`](AGENTS.md)
2. [`docs/CONTEXT.md`](docs/CONTEXT.md)
3. [`docs/TRD.md`](docs/TRD.md)
4. [`docs/PRD.md`](docs/PRD.md)
5. [`docs/internal/operations_panel.md`](docs/internal/operations_panel.md)
6. [`docs/internal/status.md`](docs/internal/status.md)
7. [`docs/implementation/README.md`](docs/implementation/README.md)
8. [`docs/README.md`](docs/README.md)

If these documents conflict, stop and reconcile the contract before changing code.

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
src/promptops     PromptOps governance, experiments, review scaffolding
src/scraper       Source-specific scraper interfaces and normalizers
src/db            Legacy SQLModel models, repository history, and schema references
src/common        Shared config, logging, telemetry, ids, errors
tests             Unit, integration, contract, resilience coverage
docs             Product, operations, promptops, and implementation docs
scripts          Worktree bootstrap and implementation-doc helpers
```

Quick ownership guide:

- `apps/web` and `src/*` are product code.
- `docs/*` is canonical documentation and workboard state.
- `scripts/*` is repo operations tooling and should stay lightweight.
- The repo root worktree is for review, docs maintenance, and coordination. Feature work should start in an agent worktree from `main`.

## Multi-Agent Workflow

The repo is set up for Codex, Claude, and Gemini to work in parallel, but only when everyone starts from the shared worktree scripts.

```bash
scripts/start_agent_task.sh --agent codex --task <task-slug>
scripts/start_agent_task.sh --agent claude --task <task-slug>
scripts/start_agent_task.sh --agent gemini --task <task-slug>
scripts/start_integration_task.sh --task <task-slug>
```

Rules:

- Always branch from `main`.
- Do not start feature work directly from the current checked-out branch.
- Do not commit feature work on `main`.
- Treat the root worktree as a coordination space, not the default implementation space.
- Merge or cherry-pick agent results into `integration/<task-slug>` first, then verify before opening a PR to `main`.
- If an agent does not have an automatic plan hook, save plans manually with `python3 scripts/implementation_docs.py save-plan ...`.

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

Offline evaluation workflow:

```bash
poetry run eval-jobs sync-dataset
poetry run eval-jobs run-experiment --experiment-prefix eval-prompt
poetry run eval-jobs promote-trace --run-id <langsmith-run-id>
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
- Prompt rendering now defaults to tagged LangSmith Prompt Hub identifiers such as `job-evaluation:staging` and `memory-summary:staging`, records both the requested tag and resolved commit hash in traces, and falls back to the in-repo template when Prompt Hub is unavailable.
- Offline prompt/model experiments can now be run against the curated LangSmith dataset fixture with `poetry run eval-jobs`.
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
