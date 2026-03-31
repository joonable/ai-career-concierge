# PromptOps

Date: 2026-03-31 (Asia/Seoul)

## Goal

PromptOps is the operating layer for prompt changes in this repository.

Its purpose is to make prompt improvement:

- smaller in scope,
- safer to ship,
- measurable through experiments,
- reviewable by both LLM judges and humans,
- and resilient to changing context quality from onboarding and future product features.

This repository's PromptOps starts as an internal module, not as a separate package. However, the structure should preserve a clean boundary so that shared pieces can later be extracted into a reusable package or project.

## In Scope

- prompt family registry and lifecycle metadata
- experiment orchestration for curated datasets
- evaluator composition
- failure taxonomy
- human review workflow contracts
- iteration records and prompt change tracking
- project-specific context normalization contracts
- LangSmith integration as the initial experiment and review backend

## Out Of Scope For The First Version

- a generic standalone PromptOps product
- a full UI application for prompt review
- automatic prompt rewriting without review
- complex policy engines for score calibration
- multi-project abstractions that are not yet proven by use

## Design Principles

### 1. Separate core from project-specific logic

The repository should distinguish between:

- reusable PromptOps operating concepts
- AI Career Concierge-specific scoring, context, and review policy

This allows us to move shared PromptOps pieces out later without untangling job-matching-specific logic.

### 2. Treat prompt text as one artifact inside a larger contract

Prompt changes should not live as raw text diffs only.

Each prompt family should be understood together with:

- output schema contract
- score or decision policy contract
- context normalization contract
- evaluator set
- review rubric

### 3. Keep external backends behind adapters

LangSmith is the initial backend for:

- experiments
- dataset sync
- compare links
- annotation and review workflows

But PromptOps should depend on an adapter boundary rather than directly hard-coding backend behavior into project logic.

### 4. Normalize context before prompt injection

Raw profile, onboarding, guideline, and job data will keep evolving.

Prompt families should consume normalized context blocks rather than raw incoming fields wherever possible. This reduces instability when upstream product features change shape or quality.

## Core vs Project-Specific Boundary

### PromptOps Core

The following concepts should stay generic enough to move into a future shared package:

- prompt family metadata
- prompt revision metadata
- experiment spec and experiment summary
- review item and review status
- failure classification interface
- iteration record
- backlog item shape for prompt improvement work
- LangSmith adapter boundary

### AI Career Concierge Project Layer

The following concepts remain specific to this repository until proven reusable:

- `job-evaluation` and `memory-summary` prompt families
- fit score policy and calibration semantics
- role alignment / must-have coverage / deal-breaker severity meaning
- onboarding and guideline normalization for job matching
- curated job evaluation dataset and scenario families
- human review rubric for job recommendation quality

## Iteration Loop

PromptOps iterations should follow a small-change loop:

1. Record baseline prompt version and experiment result.
2. Apply one focused prompt or context change.
3. Run experiment against the curated dataset.
4. Compare rule-based and LLM-judge outputs.
5. Route borderline or failed cases to human review.
6. Classify failures into taxonomy buckets.
7. Convert validated gaps into prompt, context, dataset, or feature backlog items.
8. Decide whether to promote, revise, or discard the candidate.

The unit of improvement is an iteration, not an arbitrary prompt edit.

## LangSmith Decision

LangSmith is the default backend for the first PromptOps version.

It is responsible for:

- prompt storage and version lineage
- curated dataset sync
- experiment execution and comparison
- review queue support through annotation workflows
- attaching machine and human feedback to runs

This is a repository decision, not a permanent architecture lock-in. The boundary for later extraction is the adapter module under `src/promptops/adapters/`.

## Initial Repository Layout

```text
src/promptops/
  core/
  adapters/
  projects/
    ai_career_concierge/
```

### `src/promptops/core`

Holds generic PromptOps operating models and services:

- models
- registry
- experiments
- evaluators
- reviews
- failures
- iterations
- backlog

The initial managed entities in Sprint 2 are:

- prompt family
- prompt metadata
- prompt revision
- experiment spec
- iteration record

Lifecycle stages are:

- `candidate`
- `staging`
- `production`

In Sprint 4, PromptOps experiment orchestration should wrap the existing job-eval workflow instead of replacing it. The PromptOps layer is responsible for dataset sync, experiment execution, compare-link generation, and iteration summaries, while the underlying evaluation pipeline remains in `src/agent/evals`.

### `src/promptops/adapters`

Holds integration adapters, starting with LangSmith.

### `src/promptops/projects/ai_career_concierge`

Holds this repository's prompt families, normalized context definitions, dataset bindings, evaluator bundles, review rubric, and backlog mapping rules.

In Sprint 3, job evaluation prompts should stop reading raw profile/guideline/job dictionaries directly and instead consume a normalized evaluation context contract from `projects/ai_career_concierge/context.py`.

## Definition Of Done For Sprint 1

Sprint 1 is complete when:

- `docs/PROMPTOPS.md` makes the operating model understandable,
- the `src/promptops/` package skeleton exists,
- core vs project-specific boundaries are visible in code layout,
- and the scaffold can be imported without implementation-specific coupling.
