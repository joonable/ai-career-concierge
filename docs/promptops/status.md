# PromptOps 현재 상태

날짜: 2026-03-31 (Asia/Seoul)

이 문서는 개발자와 비개발자 모두가 PromptOps의 현재 상태를 같은 위치에서 확인하기 위한 공용 상태판입니다.

웹 운영 패널에서는 `/internal/prompts`에서 같은 상태를 카드 형태로 확인할 수 있습니다.

## `job-evaluation`

### 현재 상태 스냅샷

- 현재 production tag: `job-evaluation:latest`
- 현재 staging tag: `job-evaluation:staging`
- 현재 candidate prompt: `job-evaluation`
- 현재 candidate 로컬 참조: `local-v4` (직전 후보안)
- 최신 결정: `자동화 이터레이션 시스템 도입 및 002-final 실험 완료, 지표 분석 중`

### LangSmith / 문서 / Notion 링크

- production prompt: `job-evaluation:latest`
- staging prompt: `job-evaluation:staging`
- candidate prompt: `job-evaluation` candidate lineage
- 최신 자동화 실험 리포트: [`iteration_002-final.md`](./iterations/iteration_002-final.md)
- human review queue: `job-evaluation-review`
- Notion backlog: [PromptOps Backlog](https://www.notion.so/c5fb7393ece54107b445e90bdabab642)

### 최신 실험 요약 (Iteration 002-final)

- **Pass Rate:** `0.0%` (자동 평가 기준, 키워드 불일치 위주)
- **주요 발견:** 
    - `classification_match` 및 `fit_score_band`는 안정적이나, `keyword_match` 계열에서 한/영 불일치로 인한 실패가 다수 발생.
    - 모델의 추론(Reasoning) 품질은 높으나, 평가기(Evaluator)가 기대하는 정적 키워드 형식을 벗어나는 경향이 있음.
- **기술적 진보:** `run_iteration.py` 도입으로 데이터셋 동기화부터 리포트 생성까지 자동화됨.

### 현재 해석

- 현재의 "실패"는 프롬프트의 논리적 오류보다는 **평가 지표(Metric)와 모델 답변 간의 언어 불일치**에서 기인한 것이 많습니다.
- 프롬프트를 수정하여 답변 형식을 더 엄격하게 제한하거나, 평가기 로직을 유연하게(예: 한/영 동시 지원) 개선해야 합니다.
- 자동화된 이터레이션 루프가 완성되었으므로, 이제 프롬프트 수정 후 즉시 검증이 가능합니다.

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

- 상위 기준서: [`README.md`](./README.md)
