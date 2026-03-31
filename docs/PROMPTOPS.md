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

Iteration artifacts should be written under `docs/promptops_iterations/` so each prompt family can keep a lightweight history of:

- baseline and candidate revisions
- experiment links and result deltas
- human review queue handoff
- next backlog items

## LangSmith Decision

LangSmith is the default backend for the first PromptOps version.

It is responsible for:

- prompt storage and version lineage
- curated dataset sync
- experiment execution and comparison
- review queue support through annotation workflows
- attaching machine and human feedback to runs

This is a repository decision, not a permanent architecture lock-in. The boundary for later extraction is the adapter module under `src/promptops/adapters/`.

Official LangSmith references used for Sprint 5 design:

- Annotation queues: `https://docs.langchain.com/langsmith/annotation-queues`
- Feedback configs and queue SDK: `https://docs.langchain.com/langsmith/annotation-queues-sdk`
- Attach user feedback: `https://docs.langchain.com/langsmith/attach-user-feedback`

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

In Sprint 5, review workflow contracts should define:

- which runs are routed to LLM judge vs human review
- which rubric criteria humans score
- how borderline and failure cases are selected
- how review feedback is stored and converted into backlog candidates
- how queue payloads map onto LangSmith annotation queue concepts

### `src/promptops/adapters`

Holds integration adapters, starting with LangSmith.

### `src/promptops/projects/ai_career_concierge`

Holds this repository's prompt families, normalized context definitions, dataset bindings, evaluator bundles, review rubric, and backlog mapping rules.

In Sprint 3, job evaluation prompts should stop reading raw profile/guideline/job dictionaries directly and instead consume a normalized evaluation context contract from `projects/ai_career_concierge/context.py`.

## Review Workflow Spec

### Review modes

- `llm_judge`
- `human`

### Review queue

For AI Career Concierge, the initial human review queue is:

- queue name: `job-evaluation-review`
- backend: LangSmith
- queue mode: `single`
- prompt family: `job-evaluation`

### Human rubric

The initial rubric criteria are:

- `role_alignment`
- `must_have_coverage`
- `deal_breaker_handling`
- `transferable_skill_credit`
- `summary_usefulness`

### Case selection rules

Send a case to human review when either of these is true:

- it is a borderline case
  - current default: `fit_score` between `40` and `79`, or `role_alignment = MEDIUM`
- it is a failure case
  - current default: any tracked evaluator score is below `1.0`

This keeps human review focused on ambiguous or broken cases rather than obvious passes.

### Feedback record

Review feedback should capture:

- review item id
- reviewer type (`llm_judge` or `human`)
- reviewer id when available
- rubric scores
- freeform notes
- final decision
- derived backlog candidates

### Backlog mapping

Review feedback should not stop at "good" or "bad". It should map into candidate work buckets such as:

- prompt wording gaps
- policy gaps
- context normalization gaps
- dataset truth gaps
- missing product features

## Failure Taxonomy And Backlog Rules

### Failure taxonomy

The initial taxonomy keys are:

- `prompt.role_alignment`
- `prompt.must_have_coverage`
- `prompt.transferable_skill_credit`
- `prompt.summary_usefulness`
- `dataset.gold_expectation_gap`
- `dataset.borderline_coverage_gap`
- `context.normalization_gap`
- `policy.deal_breaker_handling`
- `policy.score_band_definition`
- `feature.onboarding_signal_missing`

### Category split

PromptOps should separate failures into:

- prompt issue
- dataset issue
- context issue
- policy issue
- feature issue

This matters because the correct next action is different:

- prompt issue: change prompt wording or structure
- dataset issue: add or fix gold truth
- context issue: add or normalize an input signal
- policy issue: clarify product scoring rules first
- feature issue: collect a new signal in the product

### Backlog item format

Each backlog item should capture:

- stable item key
- category
- priority
- title
- next action
- linked taxonomy keys
- evidence from review or experiment

### Priority defaults

Default priority by category:

- `policy` -> `P0`
- `feature` -> `P1`
- `prompt` -> `P1`
- `context` -> `P1`
- `dataset` -> `P2`

### Operating rule

Review should produce actionable backlog items, not just observations.

If a reviewer says a case is wrong, PromptOps should answer:

- what kind of failure it is,
- what should change next,
- and how urgent that change is.

### Example failure backlog items

- `prompt:role-alignment`
- `prompt:must-have-coverage`
- `policy:deal-breaker-handling`
- `dataset:borderline-coverage-gap`
- `feature:onboarding-signal-missing`

## Definition Of Done For Sprint 1

Sprint 1 is complete when:

- `docs/PROMPTOPS.md` makes the operating model understandable,
- the `src/promptops/` package skeleton exists,
- core vs project-specific boundaries are visible in code layout,
- and the scaffold can be imported without implementation-specific coupling.
