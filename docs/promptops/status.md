# PromptOps 현재 상태

날짜: 2026-04-12 (Asia/Seoul)

이 문서는 개발자와 비개발자 모두가 PromptOps의 현재 상태를 같은 위치에서 확인하기 위한 공용 상태판입니다.

웹 운영 패널에서는 `/internal/prompts`에서 같은 상태를 카드 형태로 확인할 수 있습니다.
운영 패널에 보이는 golden dataset 기준은 local fixture `src/agent/evals/fixtures/job_eval_gold.json`을 read-only snapshot으로 노출한 것입니다.
평가 지표의 의미와 해석 기준은 [`metric_glossary.md`](./metric_glossary.md)에서 확인합니다.

## `job-evaluation`

### 현재 상태 스냅샷

- 현재 production tag: `job-evaluation:latest`
- 현재 staging tag: `job-evaluation:staging`
- 현재 candidate prompt: `job-evaluation`
- 현재 candidate 로컬 참조: `local-v4` (직전 후보안)
- 최신 결정: `한국어 실험 기준으로 fixture와 해석층 정렬 진행, 승격 판단은 보류`

### LangSmith / 문서 / Notion 링크

- production prompt: `job-evaluation:latest`
- staging prompt: `job-evaluation:staging`
- candidate prompt: `job-evaluation` candidate lineage
- 최신 자동화 실험 리포트: [`iteration_002-final.md`](./iterations/iteration_002-final.md)
- human review queue: `job-evaluation-review`
- Notion backlog: [PromptOps Backlog](https://www.notion.so/c5fb7393ece54107b445e90bdabab642)

### 최신 실험 요약 (Iteration 002-final)

- **Pass Rate:** `0.0%` (자동 평가 기준)
- **주요 발견:** 
    - `classification_match`와 `fit_score_band` 자체보다, 경계 사례에서 강점/우려 신호를 어떤 운영 언어로 해석할지의 기준이 더 큰 실패 요인으로 드러났습니다.
    - 인접 직무 사례에서 `role_alignment`, `must_have_coverage`, `transferable_skill_credit` 해석이 한국어 운영 문맥과 완전히 맞물리지 않아 review 난이도가 높았습니다.
- **기술적 진보:** `run_iteration.py` 도입으로 데이터셋 동기화부터 리포트 생성까지 자동화됨.

### 현재 해석

- 현재의 "실패"는 단순한 프롬프트 오류라기보다, 한국어 채용 공고 기준으로 어떤 강점과 우려를 핵심 신호로 볼지에 대한 운영 해석층이 덜 정리된 데서 많이 발생했습니다.
- 다음 기준은 영어 키워드 형식 고정보다 한국어 공고에서 역할 정렬, 필수요건 충족, 딜브레이커 처리, 전이 가능한 역량 반영을 일관되게 읽는 데 둡니다.
- 자동화된 이터레이션 루프가 완성되었으므로, 이제 한국어 fixture와 evaluator 해석을 맞춘 뒤 바로 재검증할 수 있습니다.

### 다음 backlog top 3

- `prompt:role-alignment` — 인접 직무에서 MLE 역할 정렬을 더 보수적으로 설명
- `prompt:must-have-coverage` — 한국어 공고에서 필수요건 근거를 더 분명하게 추출
- `prompt:transferable-skill-credit` — 전이 가능한 역량을 과대평가하지 않도록 기준 정리

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
- 평가 지표 기준서: [`metric_glossary.md`](./metric_glossary.md)
