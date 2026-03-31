# Fit Score Calibration Baseline

Date: 2026-03-31 (Asia/Seoul)

## Scope checked

- Prompt/schema/eval flow
  - `/Users/joon/PycharmProjects/ai-career-concierge/src/agent/schemas/evaluation_result.py`
  - `/Users/joon/PycharmProjects/ai-career-concierge/src/agent/prompts/prompt_manager.py`
  - `/Users/joon/PycharmProjects/ai-career-concierge/src/agent/evaluation_service.py`
  - `/Users/joon/PycharmProjects/ai-career-concierge/src/agent/evals/dataset_workflow.py`
  - `/Users/joon/PycharmProjects/ai-career-concierge/src/agent/evals/rule_based_evaluators.py`
  - `/Users/joon/PycharmProjects/ai-career-concierge/src/agent/evals/runner.py`
- Gold fixture
  - `/Users/joon/PycharmProjects/ai-career-concierge/src/agent/evals/fixtures/job_eval_gold.json`
- Baseline tests
  - `/Users/joon/PycharmProjects/ai-career-concierge/tests/unit/test_prompt_manager.py`
  - `/Users/joon/PycharmProjects/ai-career-concierge/tests/contract/test_llm_schema.py`
  - `/Users/joon/PycharmProjects/ai-career-concierge/tests/contract/test_slack_payload.py`

## Current repo baseline

- `LLMEvaluationResult` is on structured output v2 with:
  - `fit_score`, `summary`, `strengths`, `concerns`
  - `must_have_matches`, `deal_breaker_flags`
  - `confidence`
  - legacy-normalized aliases: `reasoning`, `must_have_hits`, `deal_breakers_found`
- Local fallback evaluation prompt is also v2.
- Prompt schema version in code is `2`.
- Default configured evaluation prompt identifier is `job-evaluation:staging`.
- Default configured memory prompt identifier is `memory-summary:staging`.
- Default configured eval dataset name is `job-eval-gold-dev`.

## Gold fixture baseline

- Current curated fixture size: `5` examples.
- Current scenarios present:
  - `strong_match`
  - `obvious_reject`
  - `borderline_case`
  - `deal_breaker_hit`
  - `must_have_mismatch`
- Current fixture outputs include:
  - `should_pass`
  - `fit_score_range`
  - `expected_must_have_matches`
  - `expected_deal_breaker_flags`
  - `expected_strength_keywords`
  - `expected_concern_keywords`
  - `expected_confidence`
- Current fixture does not yet encode explicit score-policy metadata such as:
  - `scoring_note`
  - `scenario_family`
  - `expected_role_alignment`
  - `expected_must_have_coverage`
  - `expected_deal_breaker_severity`
  - `expected_transferable_skills`

## Evaluator baseline

- Current rule-based evaluators:
  - `classification_match`
  - `fit_score_band`
  - `summary_concise`
  - `must_have_expectation`
  - `deal_breaker_expectation`
  - `strength_keywords_match`
  - `concern_keywords_match`
  - `confidence_alignment`
- Current evaluator coverage is strong for structured explanation quality.
- Current evaluator coverage is weak for diagnosing why a `fit_score_band` miss happened on borderline roles.

## Local verification

Command used:

```bash
poetry run pytest tests/unit/test_prompt_manager.py tests/contract/test_llm_schema.py tests/contract/test_slack_payload.py
```

Result:

- `7 passed`

Note:

- Running plain `pytest` in the shell failed because `sqlmodel` was not available outside the Poetry environment.

## LangSmith baseline

User-reported recent clean experiment:

- `structured-eval-retry-local-v2-57af6bfd`

User-reported compare link:

- `https://smith.langchain.com/o/a5f5f699-f384-58ec-9be0-2a39bb96969e/datasets/277c4ae5-c460-4be4-8895-732911768cd7/compare?selectedSessions=8fd2d355-6c91-46ce-b9b8-29472d0efa9e`

User-reported latest evaluation summary:

- `classification_match = 1.0`
- `summary_concise = 1.0`
- `must_have_expectation = 1.0`
- `deal_breaker_expectation = 1.0`
- `strength_keywords_match = 1.0`
- `concern_keywords_match = 1.0`
- `confidence_alignment = 1.0`
- `fit_score_band = 0.8`

Prompt/tag status to carry forward:

- `job-evaluation:latest` and `job-evaluation` point to the v2 prompt.
- `job-evaluation:staging` is reported to still point to an older commit.
- Target follow-up action: move `staging` to latest commit `1a2cd973...` in LangSmith UI before the next staged experiment run.

## Calibration problem statement

- The known failing policy area is borderline calibration for adjacent roles.
- The concrete example called out is `Data Engineer for ML Platform`.
- Current gold expectation for that case is `40~79`.
- Reported model output for that case was `30`.
- Working hypothesis: the instability is less about explanation quality and more about missing explicit score policy for:
  - adjacent-role credit
  - must-have gap penalty
  - transferable-skill credit
  - deal-breaker severity handling

## Recommended next step

- Start with score-policy documentation and borderline gold dataset expansion before changing the scoring prompt again.

## Phase 12 decision: post-processing calibration

Date: 2026-03-31 (Asia/Seoul)

### Evidence reviewed

- Baseline experiment
  - Session: `8fd2d355-6c91-46ce-b9b8-29472d0efa9e`
  - `fit_score_band = 0.8`
- Post-v3 experiment
  - Session: `d8645902-b6d4-47e3-92ab-62d75f0ab092`
  - Experiment: `structured-eval-v3-retry-local-v1-d6c4d740`
  - `fit_score_band = 0.8667`
- Before/after compare
  - `https://smith.langchain.com/o/a5f5f699-f384-58ec-9be0-2a39bb96969e/datasets/277c4ae5-c460-4be4-8895-732911768cd7/compare?selectedSessions=8fd2d355-6c91-46ce-b9b8-29472d0efa9e&selectedSessions=d8645902-b6d4-47e3-92ab-62d75f0ab092`

### What changed after v3 policy + schema + prompt work

- The main calibration target, `gold-005` (`Data Engineer for ML Platform`), moved into the expected band.
  - Previous reported output: `30`
  - Current v3 retry output: `50`
  - Current `fit_score_band` result: pass
- Overall `fit_score_band` improved from `0.8` to `0.8667` without any post-processing layer.
- `hard_reject_penalty = 1.0`, which suggests the prompt-level policy is already respecting the strongest "do not over-recommend" guardrail.

### Remaining unstable case families

The remaining misses are no longer a single generic "LLM scores badly" problem. They cluster into a few practical families:

- Adjacent infra/platform roles that still receive too much recommendation credit
  - Example: `gold-006 Senior Data Engineer, Experimentation Platform`
  - Example: `gold-011 Software Engineer, Experimentation Infrastructure`
  - Typical pattern: role alignment is not low enough to reject, but transferable skill and infra overlap may be over-weighted.
- Must-have coverage ambiguity
  - The model can now explain the gap, but borderline infra cases can still land one band too high when core production-ML ownership is weak.
- Dataset sync contamination for newly added sub-judgment evaluators
  - The LangSmith dataset sync path currently does not cleanly update existing examples with new expected fields.
  - As a result, `role_alignment_match`, `must_have_coverage_match`, `deal_breaker_severity_match`, and `transferable_skill_credit` are not yet trustworthy enough to justify a code-level calibration policy.

### Pure LLM sufficiency assessment

Current conclusion: pure LLM scoring is not fully "done", but it is already good enough to justify one more iteration before adding a score post-processor.

Reasoning:

- The most important known failure (`gold-005`) was fixed by clarifying policy in schema + prompt rather than adding deterministic score rules.
- Overall band accuracy improved with prompt/schema work alone.
- The remaining misses are concentrated in a narrow adjacent-role family, which means the next highest-leverage change is likely cleaner gold truth plus prompt refinement, not immediate calibration code.
- Because dataset truth for the new structured axes is partially contaminated, a post-processing layer added now would be tuned against noisy eval feedback.

### Candidate correction rules if calibration is still needed later

If a post-processing layer is needed after a clean rerun, the first version should stay minimal and only encode strong policy invariants:

- If `role_alignment = LOW`, do not allow the score to land in the strong-recommend band.
- If `deal_breaker_severity = HARD`, cap the score below strong-recommend territory.
- If `role_alignment = MEDIUM` and `transferable_skills = HIGH`, do not let the score collapse into the obvious-reject band by default.
- If `must_have_coverage = WEAK`, avoid promoting the role into a high-confidence recommendation unless another policy explicitly justifies it.

These are better expressed as band-oriented floor/ceiling guards than as a full hand-tuned numeric formula.

### Clamp vs rule engine decision

If calibration is introduced, prefer a small clamp-style calibration function over a rule engine.

Why:

- The product policy currently needs a few clear guardrails, not a large decision system.
- Clamp logic is easier to audit against the documented score bands.
- A rule engine would create extra policy surface area before the dataset and evaluator truth have stabilized.
- The current failure mode is "band drift on a narrow family of adjacent roles", not "many interacting business rules".

### Decision

Do not introduce post-processing calibration yet.

Instead:

- First fix the LangSmith dataset sync/upsert behavior so new expected fields are reliably applied to the curated gold set.
- Re-run the v3 experiment on a clean dataset.
- Re-check whether the remaining misses are still concentrated in adjacent infra/platform cases.

Only if those misses persist after a clean rerun should we add a small calibration function with explicit floor/ceiling guards. Do not build a general rule engine at this stage.

### Follow-up trigger

Revisit this decision if all of the following are true:

- dataset sync/upsert is fixed,
- the clean rerun still misses the same adjacent-role family,
- and prompt-only changes cannot raise `fit_score_band` further without causing regressions elsewhere.
