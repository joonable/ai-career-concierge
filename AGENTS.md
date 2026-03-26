# AGENTS.md

## Purpose

This repository builds **AI Career Concierge**, an AI-assisted job-matching system that filters noisy job postings and recommends only high-fit opportunities.

The current phase is a **single-user PoC**. All implementation decisions should prioritize getting the end-to-end loop working reliably for one primary user before expanding scope.

## Source Of Truth

When working in this repository, use documents in this order:

1. [`docs/CONTEXT.md`](/Users/joon/PycharmProjects/ai-career-concierge/docs/CONTEXT.md)
2. [`docs/TRD.md`](/Users/joon/PycharmProjects/ai-career-concierge/docs/TRD.md)
3. [`docs/PRD.md`](/Users/joon/PycharmProjects/ai-career-concierge/docs/PRD.md)

If there is a conflict:

- `CONTEXT.md` is the working summary for day-to-day implementation.
- `TRD.md` defines architecture and technical contracts.
- `PRD.md` defines product intent and business goals.

If a conflict is material, stop and resolve it explicitly rather than guessing.

## Current Product Scope

The PoC must support this loop:

1. User logs in with Google and configures a profile.
2. The system ingests job postings from target platforms.
3. Jobs pass through a 2-stage evaluation pipeline:
   - rule-based filtering
   - LLM-based deep evaluation
4. High-scoring jobs are delivered via Slack.
5. The user gives like/dislike feedback.
6. Recent dislike feedback is reused in later evaluation as short-term memory.

## Product Priorities

- Optimize for precision over recall.
- Reduce LLM cost by filtering aggressively before any model call.
- Preserve a clean feedback loop that improves future recommendations.
- Favor end-to-end operability over premature SaaS generalization.

## Confirmed Technical Stack

- Frontend: Next.js
- Backend: FastAPI
- Workflow orchestration: LangGraph
- LLM: Google Gemini Flash with structured JSON output
- Scraping: Playwright in Python async runtime
- Database and auth: Supabase PostgreSQL + Google OAuth
- ORM: SQLModel
- Scheduling: GitHub Actions cron trigger
- Tracing: LangSmith

Do not replace these without a clear reason and explicit user approval.

## Environment Separation

This project assumes explicit separation between development and production.

- Use separate Supabase projects for dev and prod.
- Use separate Slack workspaces or app credentials for dev and prod.
- Use separate OAuth credentials where required by the provider setup.
- Use separate API keys and secrets for all external integrations.
- Do not point local development to prod resources by default.

Operational rule:

- Development should be safe for testing, debugging, and scraper iteration.
- Production should be the only environment that runs real scheduled delivery unless the user explicitly enables a dev schedule.

## Folder Structure Principles

Prefer a repository layout that matches the system layers from the TRD and keeps boundaries obvious.

Recommended top-level structure as the codebase grows:

- `apps/web`
  - Next.js frontend for dashboard and onboarding
- `apps/api`
  - FastAPI backend for API routes, orchestration entrypoints, and integration handlers
- `packages/agent`
  - LangGraph workflow, prompt builders, evaluation schemas, and node implementations
- `packages/scraper`
  - Playwright-based ingestion logic and source-specific scrapers
- `packages/db`
  - SQLModel models, migrations, repository helpers, and DB setup
- `packages/common`
  - shared config, logging, constants, and typed utility modules
- `tests`
  - cross-package integration and end-to-end tests
- `docs`
  - product and technical documentation

If the project stays single-runtime Python for a while, an acceptable interim layout is:

- `src/api`
- `src/agent`
- `src/scraper`
- `src/db`
- `src/common`
- `tests`

Folder rules:

- Group by domain and responsibility, not by vague helpers.
- Keep framework entrypoints thin and push business logic into reusable modules.
- Keep Slack integration logic out of generic evaluation modules.
- Keep scraper implementations isolated per source so one broken source does not contaminate others.
- Put shared schemas and config in one predictable location rather than duplicating them across layers.

## Module Design Rules

- Prefer explicit names such as `evaluation_service.py`, `slack_notifier.py`, `pipeline_state.py`.
- Avoid catch-all files like `utils.py` when a domain-specific name is possible.
- Keep prompt-building logic separate from transport or provider clients.
- Keep API request models, domain models, and persistence models distinct when responsibilities diverge.
- Prefer pure functions for filtering, scoring normalization, and prompt assembly where possible.

## Architecture Rules

- Keep the system loosely coupled across presentation, API/orchestration, agent pipeline, and storage layers.
- Model the evaluation pipeline as a LangGraph `StateGraph`.
- Keep scraping, rule filtering, LLM evaluation, and delivery as separate concerns.
- Prefer typed models and structured outputs over ad hoc dict parsing.
- Keep schemas and APIs aligned with the feedback-driven recommendation workflow.

## Core Workflow Contract

The expected LangGraph node flow is:

1. `IngestNode`
2. `RuleFilterNode`
3. `LLMEvalNode`
4. `DeliverNode`

The shared pipeline state should include:

- `current_jobs`
- `user_context`
- `recent_memory`
- `evaluation_results`

Do not bypass rule filtering and send raw scraped jobs directly into LLM evaluation.

## Data Model Expectations

Core entities:

- `User`
- `Job`
- `Evaluation`
- `System_Log`

Minimum evaluation lifecycle:

- `PENDING`
- `RULE_REJECTED`
- `LLM_EVALUATED`

Minimum feedback states:

- `LIKE`
- `DISLIKE`

Important invariants:

- `Job.external_job_id` must be unique per source to prevent duplicate ingestion.
- Rule-based rejections must still be persisted as evaluation state.
- Dislike feedback should be storable with a reason when available.

## Required External Interfaces

Maintain compatibility with these endpoints:

- `POST /api/v1/pipeline/trigger`
- `POST /api/v1/slack/interactive-webhook`
- `GET /api/v1/users/me/dashboard`

`POST /api/v1/pipeline/trigger` must validate internal `X-API-Key`.

## Configuration And Environment Variable Rules

- Centralize configuration loading in one module per runtime.
- Read environment variables once, validate them early, and expose typed settings objects.
- Fail fast on missing required secrets in production-facing code paths.
- Keep local defaults minimal and safe.

Naming rules:

- Use uppercase snake case for all environment variables.
- Prefix variables by subsystem when useful:
  - `SUPABASE_*`
  - `GOOGLE_*`
  - `SLACK_*`
  - `LANGSMITH_*`
  - `GEMINI_*`
- Use generic names for active runtime config selected by the current environment, for example:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SLACK_BOT_TOKEN`
- Use `APP_ENV` to indicate active runtime environment, with values such as `development`, `test`, or `production`.
- Prefer separate env files like `.env.development` and `.env.production` over suffixing every variable with `_DEV` and `_PROD` inside application code.
- Reserve explicit suffixes like `_TEST` only for isolated test configuration when needed.

Secret handling rules:

- Never hardcode secrets.
- Never commit real `.env` files.
- Never reuse prod secrets in development or tests.
- Treat service role keys and webhook signing secrets as high sensitivity.

## Reliability Requirements

- Scraping failure on one platform must not stop the entire pipeline.
- Failed sources should be skipped, logged, and surfaced operationally.
- Important failures should be recordable in `System_Log`.
- The system should degrade gracefully when a scraper breaks.

## Scope Guardrails

Do not spend time on these before the PoC loop works:

- multi-tenant SaaS complexity
- resume upload and RAG onboarding
- advanced dashboard features beyond recommendation review and feedback
- broad optimization for many job platforms unless required for the core loop

## Implementation Guidance

- Prefer simple designs that can be extended later.
- Avoid over-engineering abstractions before there is a working vertical slice.
- Build the smallest useful version of each layer that preserves the architecture contract.
- Keep LLM usage narrow, typed, and easy to observe.
- Make failure paths explicit, especially around scraping and external integrations.
- Centralize environment loading so env-specific branching is explicit and testable.
- Name configuration fields so it is obvious whether a value is shared, dev-only, or prod-only.
- Add seams that make scraper, LLM, and Slack integrations mockable in tests.

## Testing Priorities

Testing should follow the product risk, not just line coverage.

Highest priority:

- Rule-based filtering behavior
- Evaluation status transitions
- Feedback persistence and memory summarization behavior
- Configuration loading and environment separation safeguards
- Pipeline trigger authentication with `X-API-Key`

Second priority:

- LLM structured output parsing and validation
- Slack payload formatting and webhook handling
- Scraper normalization and deduplication behavior
- Dashboard response shaping

Lower priority in the earliest PoC:

- broad UI snapshot coverage
- exhaustive scraper tests for many platforms before those platforms exist
- low-value unit tests for trivial framework wiring

Test shape guidance:

- Put pure logic under fast unit tests first.
- Add integration tests for DB-backed evaluation flows and API handlers.
- Add contract tests around structured LLM outputs and Slack request payloads.
- For scrapers, prefer fixture-based parsing tests plus a small number of guarded live checks if needed.
- Add regression tests for any bug in filtering, scoring, feedback, or deduplication.

Minimum expectation for new feature work:

- New business logic should ship with at least one automated test unless the code is temporary scaffolding.
- Bug fixes should include a regression test when practical.
- If a test is intentionally skipped, document why in the final update.

## Working Norms For Agents

- Read `docs/CONTEXT.md` before making substantial changes.
- Preserve the current stack and architecture unless the user asks for a change.
- When adding new modules, keep names explicit and aligned with product concepts.
- When uncertain, choose the path that best supports:
  - end-to-end PoC operability
  - low LLM cost
  - feedback-aware recommendation quality
  - future SaaS extensibility without present complexity

## Documentation Rule

If implementation changes the architecture, API contract, core data model, or workflow assumptions, update the relevant docs in:

- `docs/CONTEXT.md`
- `docs/TRD.md`
- `docs/PRD.md`

Keep `docs/CONTEXT.md` concise and implementation-oriented.

## Repository Conventions

- Keep secrets out of git.
- Commit only templates such as `.env.example`, never real `.env` files.
- When adding config, prefer a structure that can cleanly support both `.env.development` and `.env.production`.
- Keep generated artifacts and local caches out of version control.
- Keep documentation close to the implementation when it defines contracts, but keep high-level product and architecture docs under `docs/`.
