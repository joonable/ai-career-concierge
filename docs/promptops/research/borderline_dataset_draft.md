# 경계 사례 데이터셋 초안

Date: 2026-04-12 (Asia/Seoul)

## 목적

이 문서는 `fit_score` calibration을 위한 borderline 골드 데이터셋(gold dataset) 초안입니다. 아직 fixture에 반영하기 전의 정책 설계 단계이며, 각 예시는 이후 [`src/agent/evals/fixtures/job_eval_gold.json`](/Users/joon/PycharmProjects/ai-career-concierge/src/agent/evals/fixtures/job_eval_gold.json)로 옮기기 쉬운 형태로 정리합니다.

기본 사용자 기준:

- Role: `Machine Learning Engineer`
- Years of experience: `6`
- Must-haves: `Python`, `SQL`, `MLOps`
- Deal-breakers: `contract-only`, `onsite-only`
- Notification threshold: `80`

## 시나리오 계열

- `ml_adjacent_data_engineer`
- `backend_model_serving`
- `applied_scientist_without_ownership`
- `analytics_infra`
- `mlops_heavy_weak_modeling`
- `title_mismatch_skill_overlap`

## 초안 예시

### 1. ML-adjacent data engineer

- Family: `ml_adjacent_data_engineer`
- Working title: `Data Engineer for ML Platform`
- Job sketch:
  - Own warehouse pipelines and feature-ready datasets for ML teams.
  - Heavy SQL and Python.
  - Supports model consumers but does not own model serving or MLOps platform decisions.
- Expected fit score band: `40~59`
- Expected strength keywords:
  - `python`
  - `sql`
  - `data pipeline`
- Expected concern keywords:
  - `mlops`
  - `serving`
  - `ownership`
- Expected confidence: `MEDIUM`
- Scoring note:
  - Strong transferable data skills exist, but direct MLE ownership is weak and a core must-have axis is missing.

### 2. Senior analytics data engineer with experimentation support

- Family: `ml_adjacent_data_engineer`
- Working title: `Senior Data Engineer, Experimentation Platform`
- Job sketch:
  - Builds event pipelines, experiment datasets, and metrics tables.
  - Strong SQL, Python, and A/B testing infra.
  - Little evidence of model deployment or ML operations ownership.
- Expected fit score band: `40~59`
- Expected strength keywords:
  - `python`
  - `sql`
  - `experimentation`
- Expected concern keywords:
  - `mlops`
  - `deployment`
  - `model serving`
- Expected confidence: `MEDIUM`
- Scoring note:
  - Relevant adjacent infrastructure experience gives exploration value, but the role is still analytics/data-first rather than MLE-first.

### 3. Backend engineer for model serving APIs

- Family: `backend_model_serving`
- Working title: `Senior Backend Engineer, Model Serving`
- Job sketch:
  - Owns Python services for inference APIs, latency, scaling, and deployment workflows.
  - Works closely with ML teams but does not train models directly.
  - Production ownership is strong.
- Expected fit score band: `60~79`
- Expected strength keywords:
  - `python`
  - `serving`
  - `deployment`
- Expected concern keywords:
  - `modeling`
  - `training`
- Expected confidence: `MEDIUM`
- Scoring note:
  - This is adjacent but operationally close to MLE, so it should score above exploratory adjacent roles even if pure modeling scope is limited.

### 4. Platform backend role with inference infra and weak ML context

- Family: `backend_model_serving`
- Working title: `Backend Platform Engineer, AI Runtime`
- Job sketch:
  - Builds runtime APIs, queueing, observability, and rollout tooling for AI products.
  - Uses Python and cloud infra heavily.
  - ML context exists, but role centers more on backend platform than end-to-end ML systems.
- Expected fit score band: `60~79`
- Expected strength keywords:
  - `python`
  - `platform`
  - `inference`
- Expected concern keywords:
  - `sql`
  - `modeling`
  - `ownership scope`
- Expected confidence: `MEDIUM`
- Scoring note:
  - Strong production overlap and transferable infra ownership justify reviewable status, but must-have coverage is not clean enough for strong recommendation.

### 5. Applied scientist with experimentation but no production ownership

- Family: `applied_scientist_without_ownership`
- Working title: `Applied Scientist, Ranking`
- Job sketch:
  - Works on offline experiments, model iteration, and evaluation for ranking systems.
  - Strong Python and modeling relevance.
  - SQL depth and MLOps ownership are unclear.
- Expected fit score band: `60~79`
- Expected strength keywords:
  - `python`
  - `ranking`
  - `experimentation`
- Expected concern keywords:
  - `sql`
  - `mlops`
  - `production ownership`
- Expected confidence: `MEDIUM`
- Scoring note:
  - High topical relevance should keep this above low-score adjacent roles, but missing deployment and platform ownership should prevent `80+`.

### 6. Research-heavy scientist role with minimal shipping responsibility

- Family: `applied_scientist_without_ownership`
- Working title: `Research Scientist, Personalization`
- Job sketch:
  - Focuses on model prototyping, papers, and offline evaluation.
  - Some Python and ML relevance.
  - Very little evidence of production system ownership or MLOps.
- Expected fit score band: `40~59`
- Expected strength keywords:
  - `python`
  - `personalization`
  - `modeling`
- Expected concern keywords:
  - `production`
  - `mlops`
  - `ownership`
- Expected confidence: `MEDIUM`
- Scoring note:
  - It is ML-adjacent and skill-overlapping, but too research-leaning to treat as a strong practical MLE match.

### 7. Analytics infra role with experimentation systems

- Family: `analytics_infra`
- Working title: `Software Engineer, Experimentation Infrastructure`
- Job sketch:
  - Builds experimentation tooling, metrics services, and offline analysis workflows.
  - Strong SQL and Python.
  - No direct model lifecycle or serving ownership.
- Expected fit score band: `40~59`
- Expected strength keywords:
  - `python`
  - `sql`
  - `experimentation`
- Expected concern keywords:
  - `mlops`
  - `serving`
  - `model lifecycle`
- Expected confidence: `MEDIUM`
- Scoring note:
  - Useful adjacent systems work, but still one step removed from end-to-end MLE execution.

### 8. MLOps-heavy platform role with limited modeling depth

- Family: `mlops_heavy_weak_modeling`
- Working title: `MLOps Engineer`
- Job sketch:
  - Owns training pipelines, deployment automation, model registry, CI/CD, and monitoring.
  - Strong Python and MLOps.
  - SQL use is present but not central, and modeling depth is limited.
- Expected fit score band: `60~79`
- Expected strength keywords:
  - `python`
  - `mlops`
  - `deployment`
- Expected concern keywords:
  - `modeling`
  - `sql depth`
- Expected confidence: `MEDIUM`
- Scoring note:
  - Strong must-have overlap and real production ownership make this clearly reviewable, but weak modeling breadth keeps it below top-tier match.

### 9. AI title with mostly data platform work

- Family: `title_mismatch_skill_overlap`
- Working title: `AI Platform Engineer`
- Job sketch:
  - Title sounds close to MLE.
  - Actual work is batch ETL, internal tooling, and warehouse performance tuning.
  - Python and SQL are present, but model operations are marginal.
- Expected fit score band: `40~59`
- Expected strength keywords:
  - `python`
  - `sql`
  - `platform`
- Expected concern keywords:
  - `mlops`
  - `serving`
  - `title mismatch`
- Expected confidence: `HIGH`
- Scoring note:
  - The title should not inflate the score when the responsibilities are materially more data platform than ML engineering.

### 10. Full-stack product role with strong ML tooling overlap

- Family: `title_mismatch_skill_overlap`
- Working title: `Software Engineer, AI Developer Experience`
- Job sketch:
  - Builds SDKs, prompt tooling, eval workflows, and internal services for ML teams.
  - Strong Python and production systems exposure.
  - Limited SQL and limited direct model deployment ownership.
- Expected fit score band: `60~79`
- Expected strength keywords:
  - `python`
  - `tooling`
  - `ml workflow`
- Expected concern keywords:
  - `sql`
  - `deployment ownership`
  - `direct mle scope`
- Expected confidence: `MEDIUM`
- Scoring note:
  - Although the title is not classic MLE, the practical overlap with ML workflows and platform tooling is high enough to justify human review.

## 커버리지 요약

- Total draft examples: `10`
- Distribution by expected band:
  - `40~59`: 5
  - `60~79`: 5
- Distribution by family:
  - `ml_adjacent_data_engineer`: 2
  - `backend_model_serving`: 2
  - `applied_scientist_without_ownership`: 2
  - `analytics_infra`: 1
  - `mlops_heavy_weak_modeling`: 1
  - `title_mismatch_skill_overlap`: 2

## 다음 단계 메모

- These examples are intentionally practical and close to realistic hiring-market ambiguity.
- The next step is to encode these drafts into fixture schema fields such as:
  - `expected_fit_score_band`
  - `expected_strength_keywords`
  - `expected_concern_keywords`
  - `expected_confidence`
  - `scoring_note`
  - `scenario_family`
