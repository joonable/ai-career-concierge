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

## Environment Strategy

- Separate dev and prod environments from the start.
- Dev can use local DB or Supabase dev project with Slack test workspace.
- Prod uses dedicated Supabase and Slack environments plus GitHub Actions CI/CD and scheduling.
- Never share database, Slack workspace, OAuth credentials, or API keys between dev and prod.
- Keep environment variables explicitly split so local development cannot accidentally point to prod resources.
- Treat scheduled pipeline execution as prod-only by default unless a dedicated dev schedule is intentionally configured.
- Prefer naming that makes environment targets obvious, for example `SUPABASE_URL_DEV` at setup time or separate `.env.development` and `.env.production` files at app level.

## Guardrails For Future Work

- Do not introduce LLM evaluation before rule filtering is in place.
- Do not optimize for multi-tenant SaaS complexity before the single-user PoC loop works.
- Do not depend on fragile scraper success for overall pipeline completion.
- Keep schemas and APIs aligned with the feedback-driven recommendation loop.
- Prefer structured outputs and typed models over free-form parsing.

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
