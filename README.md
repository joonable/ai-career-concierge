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

## Current Scope

The current goal is a single-user PoC that supports:

- login and onboarding
- job ingestion
- rule-based filtering
- LLM evaluation
- Slack delivery
- user feedback and short-term memory reuse
