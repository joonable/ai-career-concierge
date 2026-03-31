# PromptOps 현재 상태

날짜: 2026-03-31 (Asia/Seoul)

이 문서는 개발자와 비개발자 모두가 PromptOps의 현재 상태를 같은 위치에서 확인하기 위한 공용 상태판입니다.

웹 운영 패널에서는 `/internal/promptops`에서 같은 상태를 카드 형태로 확인할 수 있습니다.

## `job-evaluation`

### 현재 상태 스냅샷

- 현재 production tag: `job-evaluation:latest`
- 현재 staging tag: `job-evaluation:staging`
- 현재 candidate prompt: `job-evaluation`
- 현재 candidate 로컬 참조: `local-v4` (직전 후보안)
- 최신 결정: `최신 staging 프롬프트 1회 검증 완료, 승격 보류`

### LangSmith / 문서 / Notion 링크

- production prompt: `job-evaluation:latest`
- staging prompt: `job-evaluation:staging`
- candidate prompt: `job-evaluation` candidate lineage
- 직전 candidate vs 최신 staging 검증 compare: [compare link](https://smith.langchain.com/o/a5f5f699-f384-58ec-9be0-2a39bb96969e/datasets/277c4ae5-c460-4be4-8895-732911768cd7/compare?selectedSessions=4906f684-12db-4c1a-88d0-782d25f5bbda&selectedSessions=91e3e1bf-e2a1-426c-a155-ce616568eabd)
- latest iteration report: [`job_evaluation_iteration_001.md`](./promptops_iterations/job_evaluation_iteration_001.md)
- human review queue: `job-evaluation-review`
- Notion backlog: [PromptOps Backlog](https://www.notion.so/c5fb7393ece54107b445e90bdabab642)

### 최신 실험 요약

- 최신 `job-evaluation:staging` 1회 검증 run: `promptops-latest-local-v1-b9ea2745`
- `fit_score_band`: `0.9333`
- `classification_match`: `1.0`
- `deal_breaker_severity_match`, `hard_reject_penalty`, `summary_concise`: 모두 `1.0`
- 약한 축: `concern_keywords_match 0.2667`, `confidence_alignment 0.4`, `strength_keywords_match 0.2`
- 중간 수준 축: `role_alignment_match 0.6667`, `transferable_skill_credit 0.6667`, `must_have_coverage_match 0.7333`

### 현재 해석

- 최신 staging 프롬프트는 점수 밴드와 분류 일관성은 충분히 안정적인 편입니다.
- 다만 설명형 evaluator, 특히 concern/confidence/strength 관련 축은 여전히 흔들립니다.
- 따라서 바로 승격하기보다 human review와 다음 prompt 보강을 거친 뒤 재판단하는 편이 안전합니다.

### 다음 backlog top 3

- `prompt:role-alignment`
- `prompt:must-have-coverage`
- `prompt:transferable-skill-credit`

## 역할별 사용법

### 개발자

1. current stage snapshot을 확인한다.
2. compare 링크를 열어 baseline/candidate 차이를 본다.
3. iteration 기록에서 해석과 blocker를 읽는다.
4. review queue와 Notion backlog를 확인한다.

### PM / 운영자

1. 최신 결정과 현재 해석을 확인한다.
2. compare 링크와 review queue를 필요 시 연다.
3. iteration 기록에서 왜 보류/유지되었는지 읽는다.
4. Notion backlog에서 다음 작업 상태를 확인한다.

## 참고 문서

- 상위 기준서: [`PROMPTOPS.md`](./PROMPTOPS.md)
