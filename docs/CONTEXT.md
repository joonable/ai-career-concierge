# Project Context

## Purpose

AI Career Concierge is an AI-driven job-matching system that reduces job-posting noise and curates only high-fit roles for each user. The current phase is a PoC focused on a single primary user profile: the developer building the product, a 5-6 year MLE.

## Current Product Scope

The PoC should support the core loop end to end:

1. User logs in and sets profile, must-haves, and deal-breakers.
2. The system ingests new job postings from target platforms.
3. Jobs go through a 2-stage evaluation pipeline:
   - Rule-based filtering first.
   - LLM-based deep evaluation only for jobs that pass rules.
4. High-scoring jobs are delivered via Slack.
5. The user leaves like/dislike feedback.
6. Recent negative feedback is reused as short-term memory in future evaluations.

## Product Priorities

- Optimize for recommendation precision over recall.
- Minimize LLM cost by aggressively filtering before model calls.
- Keep the first version operational for one user before designing for broad SaaS scale.
- Make feedback materially improve next-day recommendations.

## Confirmed Tech Stack

- Frontend: Next.js
- Backend API: FastAPI
- Agent orchestration: LangGraph
- LLM provider: Google Gemini Flash with structured JSON output
- Scraping: Playwright with Python async execution
- Database and auth: Supabase PostgreSQL with Google OAuth
- ORM: SQLModel
- Scheduler: GitHub Actions cron trigger
- Tracing: LangSmith

## Current Implementation Layout

The repository keeps the backend in a Python `src/*` layout and isolates the frontend in `apps/web`.

- `apps/web`
  - Next.js App Router frontend
  - `src/app` holds route entrypoints such as `/login`, `/auth/callback`, `/onboarding`, and `/dashboard`
  - `src/components` holds page-specific UI such as auth, onboarding, and dashboard components
  - `src/lib` holds Supabase auth helpers, API client code, and frontend runtime adapters
- `src/api`
  - FastAPI routes, schemas, dependencies, thin application services
  - Auth, profile, dashboard, feedback, and pipeline runtime use Supabase Auth plus the Supabase Data API
- `src/agent`
  - LangGraph workflow, node implementations, prompts, typed pipeline state
- `src/scraper`
  - base scraper interface, normalizer, source registry, source-specific scrapers
- `src/db`
  - Legacy SQLModel models, repository history, and schema references retained during the PoC transition
- `src/common`
  - typed config, logging, telemetry, ids, and shared errors
- `tests`
  - unit, integration, contract, and resilience tests

## Core Business Logic

### Stage 1: Rule-Based Filter

This stage should run before any LLM call.

- Exclude already evaluated jobs.
- Filter by job title relevance.
- Filter by experience/seniority fit.

Jobs rejected here should be stored with `RULE_REJECTED` status.

### Stage 2: LLM Deep Evaluation

This stage only runs for jobs that passed rule filtering.

- Analyze deal-breakers in context.
- Infer whether must-haves are satisfied.
- Assign a fit score from 1 to 100.
- Generate a short recommendation reason, around 2 lines.

Jobs completed here should be stored with `LLM_EVALUATED` status.

### Feedback Loop

- Users can mark a recommendation as `LIKE` or `DISLIKE`.
- `DISLIKE` should support storing a rejection reason.
- Recent accumulated negative feedback should be summarized and injected into later evaluations as short-term memory.

## Core Data Model

### User

- Identity: `id`, `oauth_id`, `email`
- Profile data in JSONB: role, years of experience, tech stack, etc.
- Guidelines in JSONB: must-haves and deal-breakers

### Job

- Identity: `id`, `platform`, `external_job_id`
- Source uniqueness must be enforced with `external_job_id`
- Main fields: `title`, `company`, `jd_raw_text`, `url`

### Evaluation

- Links `user_id` and `job_id`
- Lifecycle status:
  - `PENDING`
  - `RULE_REJECTED`
  - `LLM_EVALUATED`
- Main fields: `fit_score`, `reasoning`, `user_feedback`

### System_Log

- Store pipeline failures, scraping errors, and notable system events.

## LangGraph Workflow Contract

The pipeline should be modeled as a LangGraph `StateGraph` with this shared state:

- `current_jobs`: collected jobs queue
- `user_context`: profile and guideline data loaded from DB
- `recent_memory`: summarized recent dislike feedback
- `evaluation_results`: finalized evaluation outputs

Expected node flow:

1. `IngestNode`
2. `RuleFilterNode`
3. `LLMEvalNode`
4. `DeliverNode`

## External Interfaces

### Required API Endpoints

- `POST /api/v1/pipeline/trigger`
  - Called by GitHub Actions on schedule
  - Must validate internal `X-API-Key`
- `POST /api/v1/slack/interactive-webhook`
  - Receives Slack button actions
  - Updates evaluation feedback state
- `GET /api/v1/users/me/dashboard`
  - Returns personalized recommendation data for the dashboard

### Scaffold Endpoints Added For The PoC Loop

- `GET /api/v1/users/me/profile`
  - Returns the current user profile and notification settings in a canonical nested shape
- `PUT /api/v1/users/me/profile`
  - Updates profile data, guidelines, and notification settings
  - Accepts onboarding fields for role, years, must-haves, deal-breakers, and minimum fit score
  - Derives `profile_data.title_keywords` from `role` when omitted and defaults `notification_settings.delivery_channel` to `slack`
- `POST /api/v1/evaluations/{evaluation_id}/feedback`
  - Stores like or dislike feedback from the dashboard flow

### Current Auth Contract

- Web login flow is `/login -> Google OAuth -> /auth/callback -> /dashboard`.
- The dashboard becomes the first landing page and surfaces whether onboarding is still required.
- Web login uses Supabase Google OAuth and stores the resulting session with the App Router SSR cookie pattern.
- Protected web routes such as `/onboarding` and `/dashboard` require a valid Supabase session.
- Backend user endpoints require `Authorization: Bearer <Supabase access token>`.
- Backend authentication verifies Supabase JWTs against the project JWKS and extracts `sub` plus `email`.
- Backend auth-adjacent routes and pipeline persistence currently use the Supabase Data API with `SUPABASE_SERVICE_ROLE_KEY`.

## Definition Of Done

- A feature is not complete until code, automated tests, and affected docs or config references are updated together.
- If behavior changes, logging and error handling should be reviewed as part of the same delivery.
- Implementation-only work is not considered complete.

## Migration Guardrails

- Treat schema changes as contract changes.
- Keep database schema, application models, lifecycle enums, and affected docs or tests in sync.
- Any meaningful schema change should include a migration path and a rollback or compatibility consideration.

## API Change Guardrails

- Treat request and response schemas, auth behavior, webhook payloads, and status enums as stable contracts.
- If an API contract changes, update docs and automated tests in the same change.
- Check downstream impact on the dashboard, Slack flows, and scheduled pipeline triggers before finalizing the change.

## Delivery Requirements

- Primary notification channel is Slack.
- Slack messages should include:
  - job title
  - company name
  - fit score
  - short reasoning
  - deep link to the web dashboard

## Reliability Rules

- Scraping failure on one platform must not stop the full pipeline.
- Failed platforms should be skipped and logged.
- Operational failures should be stored in `System_Log`.
- Important failures should be reportable to an admin Slack channel such as `#system-alerts`.

## Observability Guardrails

- Each pipeline run should be traceable with a `run_id` or `trace_id`.
- Important logs should capture the relevant subset of `user_id`, `job_id`, `platform`, `status`, and `error_type`.
- Scraper failures, evaluation state transitions, LLM calls, Slack delivery, and webhook actions should be observable without exposing secrets or unnecessary PII.

## Prompt Management Guardrails

- Keep prompts modular and traceable instead of scattering them inline across the codebase.
- If a structured output schema changes, update the prompt instructions, parser or validator logic, and tests together.

## Environment Strategy

- Separate dev and prod environments from the start.
- Dev should default to a dedicated Supabase dev project plus a Slack test workspace.
- Prod uses dedicated Supabase and Slack environments plus GitHub Actions CI/CD and scheduling.
- Never share database, Slack workspace, OAuth credentials, or API keys between dev and prod.
- Keep environment variables explicitly split so local development cannot accidentally point to prod resources.
- Treat scheduled pipeline execution as prod-only by default unless a dedicated dev schedule is intentionally configured.
- Standardize on `APP_ENV` plus separate `.env.development`, `.env.test`, and `.env.production` files.
- Use local SQLite only for isolated tests or temporary bootstrapping, not as the standard dev runtime path.

Current scaffold defaults:

- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY` are the required backend runtime credentials for the PoC runtime path.
- The backend also reads `WEB_ORIGIN` to allow authenticated browser requests from the Next.js web app.
- `DATABASE_URL` is now a legacy optional setting for direct Postgres tooling only, not a required runtime dependency.
- `ALLOW_DEV_SCHEDULE=false` keeps non-prod scheduling disabled unless explicitly enabled.
- The web app reads `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_SUPABASE_URL`, and `NEXT_PUBLIC_SUPABASE_ANON_KEY`.

## Guardrails For Future Work

- Do not introduce LLM evaluation before rule filtering is in place.
- Do not optimize for multi-tenant SaaS complexity before the single-user PoC loop works.
- Do not depend on fragile scraper success for overall pipeline completion.
- Keep schemas and APIs aligned with the feedback-driven recommendation loop.
- Prefer structured outputs and typed models over free-form parsing.
- Treat test coverage as part of feature delivery, not as follow-up work.
- Any meaningful feature implementation or behavior change should ship with automated tests that cover the expected behavior.
- Bug fixes should add or update regression tests whenever practical.

## Deferred Or Later-Phase Ideas

- Resume PDF upload with RAG-based onboarding autofill
- Broader SaaS support for multiple tech workers beyond the initial PoC user
- More advanced dashboard workflows beyond the core recommendation and feedback cycle

## Working Assumption

When making implementation decisions, prefer the simplest design that preserves:

- end-to-end PoC operability
- low LLM cost
- feedback-aware recommendation quality
- future extensibility into a SaaS architecture
- the current hybrid layout of backend `src/*` plus frontend `apps/web`
