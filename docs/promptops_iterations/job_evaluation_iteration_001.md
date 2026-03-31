# Job Evaluation Iteration 001

Date: 2026-03-31 (Asia/Seoul)

## 1. Iteration 개요

Run the first end-to-end PromptOps iteration for the `job-evaluation` prompt family with one small prompt change, a curated experiment rerun, LLM-judge comparison, and a human review queue handoff.

### Prompt Family

- family: `job-evaluation`
- baseline prompt tag: `job-evaluation:staging`
- candidate prompt tag: `job-evaluation`
- local baseline reference: `local-v3`
- local candidate reference: `local-v4`
- lifecycle stage under test: `candidate`

## 2. Baseline

- dataset: `job-eval-gold-dev`
- fixture: `src/agent/evals/fixtures/job_eval_gold.json`
- baseline experiment: `promptops-baseline-local-v3-a59d3c59`
- baseline session id: `54971cd3-fcee-4dc1-bb7c-ca7f9abb6c59`
- baseline compare link: [baseline compare](https://smith.langchain.com/o/a5f5f699-f384-58ec-9be0-2a39bb96969e/datasets/277c4ae5-c460-4be4-8895-732911768cd7/compare?selectedSessions=54971cd3-fcee-4dc1-bb7c-ca7f9abb6c59)
- dataset sync result: `created=0`, `updated=15`, `skipped=0`

## 3. Candidate 변경

Candidate revision `local-v4` added one narrower instruction to the adjacent-role scoring section:

- experimentation infra, data platform, and analytics infra roles should default to `40~59` when direct model training, serving, or deployment ownership is weak
- only strong extra evidence should push those roles into `60+`

This was intentionally a single-line policy change rather than a broad prompt rewrite.

## 4. Candidate 실험

- candidate experiment: `promptops-candidate-local-v4-bcba8f4f`
- candidate session id: `4906f684-12db-4c1a-88d0-782d25f5bbda`
- candidate compare link: [candidate compare](https://smith.langchain.com/o/a5f5f699-f384-58ec-9be0-2a39bb96969e/datasets/277c4ae5-c460-4be4-8895-732911768cd7/compare?selectedSessions=4906f684-12db-4c1a-88d0-782d25f5bbda)
- combined compare link: [baseline vs candidate](https://smith.langchain.com/o/a5f5f699-f384-58ec-9be0-2a39bb96969e/datasets/277c4ae5-c460-4be4-8895-732911768cd7/compare?selectedSessions=54971cd3-fcee-4dc1-bb7c-ca7f9abb6c59&selectedSessions=4906f684-12db-4c1a-88d0-782d25f5bbda)
- dataset sync result: `created=0`, `updated=15`, `skipped=0`

## 5. 핵심 결과

| Metric | Baseline (`local-v3`) | Candidate (`local-v4`) | Change |
| --- | ---: | ---: | ---: |
| `fit_score_band` | 0.6667 | 0.8000 | +0.1333 |
| `classification_match` | 0.8667 | 0.9333 | +0.0666 |
| `must_have_expectation` | 0.9333 | 0.8667 | -0.0666 |
| `deal_breaker_expectation` | 1.0000 | 0.9333 | -0.0667 |
| `role_alignment_match` | 0.7333 | 0.6000 | -0.1333 |
| `must_have_coverage_match` | 0.8667 | 0.8000 | -0.0667 |
| `deal_breaker_severity_match` | 0.9333 | 0.9333 | 0.0000 |
| `transferable_skill_credit` | 0.8667 | 0.8000 | -0.0667 |
| `hard_reject_penalty` | 1.0000 | 1.0000 | 0.0000 |
| `confidence_alignment` | 0.5333 | 0.5333 | 0.0000 |

### Interpretation

- The candidate prompt improved the primary target metric `fit_score_band` from `0.6667` to `0.8000`.
- `classification_match` also improved, which suggests the narrower infra-role instruction did not destabilize top-level recommendation classes.
- The main regressions were in `role_alignment_match`, `must_have_coverage_match`, `must_have_expectation`, and `transferable_skill_credit`.
- This means the new wording helped score-band selection but may have over-compressed some adjacent-role reasoning and made structured sub-judgment labels less consistent.

## 6. Human Review

- queue name: `job-evaluation-review`
- queue id: `a1438ae9-2449-4798-94f1-0243ab9b1e18`
- backend: LangSmith annotation queue
- runs added: `15`

The queue contains borderline cases and failed candidate runs selected with this rule:

- `fit_score` between `40` and `79`
- or `role_alignment = MEDIUM`
- or any tracked evaluator score below `1.0`

### Runs Sent To Human Review

- `a20df58e-b997-4a21-9c59-8c62284520c7` `Senior Machine Learning Engineer`
- `0a6be6e6-a9d0-46af-8ae4-7af130504715` `Frontend Engineer`
- `13665ea6-8805-43a0-a69d-b0d061c86a81` `Applied Scientist`
- `a99b24c6-f5a2-4b77-8556-b1b0d03d7e13` `ML Platform Engineer`
- `8b35e988-db33-4fe8-b44a-e6945c51af42` `Data Engineer for ML Platform`
- `9994ea75-4769-401a-baee-bc8165f1b4d6` `Senior Data Engineer, Experimentation Platform`
- `cdc7faaa-5145-49ad-9ef4-b62f284623f5` `Senior Backend Engineer, Model Serving`
- `564eff8d-770d-4445-a369-8030bad6cf66` `Backend Platform Engineer, AI Runtime`
- `78826cac-73da-4004-b14c-c5f6222d2c37` `Applied Scientist, Ranking`
- `8ed6dede-2168-4bae-bfde-47f70077976a` `Research Scientist, Personalization`
- `e7441209-81df-4059-9729-95692bc60750` `Software Engineer, Experimentation Infrastructure`
- `efbca094-c3e2-4b19-95b4-978e03882153` `MLOps Engineer`
- `480b76fe-6b11-4abb-9fd9-be7f44804d48` `AI Platform Engineer`
- `7b082634-6f18-4c84-a88d-3c17ea1a5f29` `Software Engineer, AI Developer Experience`
- `147e32f5-0264-4413-83fb-8374a3ce36d8` `Machine Learning Infra Engineer`

## 8. Next Backlog

These items should be treated as the immediate follow-up candidates for the next PromptOps iteration.

### `prompt:role-alignment`

- priority: `P1`
- why: `role_alignment_match` dropped from `0.7333` to `0.6000`
- action: refine how adjacent infra roles map to `LOW` vs `MEDIUM` alignment without undoing the better score band behavior

### `prompt:must-have-coverage`

- priority: `P1`
- why: `must_have_coverage_match` and `must_have_expectation` both regressed
- action: tighten instructions so must-have gaps are still credited separately from transferable skill overlap

### `prompt:transferable-skill-credit`

- priority: `P1`
- why: `transferable_skill_credit` regressed while infra-role banding improved
- action: clarify that transferable skill credit should remain visible even when score bands stay conservative

### `prompt:summary-usefulness`

- priority: `P1`
- why: several candidate runs still missed `strength_keywords_match` or `concern_keywords_match`
- action: improve explanation wording only after role-alignment and must-have behavior are restabilized

## 7. Decision

Iteration 001 is a successful PromptOps cycle because it completed the full loop:

1. baseline snapshot recorded
2. one small prompt diff applied
3. curated experiment rerun
4. LLM-judge comparison captured
5. human review queue created
6. next backlog items registered

The candidate revision should stay in `candidate` stage for now. It improved the main score-band target, but it should not be promoted until human review confirms whether the role-alignment and must-have regressions are acceptable.
