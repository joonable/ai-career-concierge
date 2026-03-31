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
