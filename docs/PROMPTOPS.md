# PromptOps

날짜: 2026-03-31 (Asia/Seoul)

## 문서 목적

이 문서는 AI Career Concierge 저장소에서 PromptOps를 어떻게 운영할지 정의하는 기준서입니다.

PromptOps의 목적은 프롬프트를 단순 텍스트 자산이 아니라 다음 요소를 포함한 운영 대상로 관리하는 것입니다.

- 버전과 lifecycle
- 실험과 비교
- LLM judge와 human review
- failure 분석
- 다음 iteration backlog

이 문서는 구현 히스토리나 스프린트 기록이 아니라, 현재 기준의 운영 원칙과 책임 경계를 설명합니다.

## PromptOps의 목표

이 저장소에서 PromptOps는 다음 문제를 해결해야 합니다.

- 프롬프트 변경을 작은 단위로 안전하게 진행한다.
- 프롬프트 변경 효과를 curated dataset 실험으로 측정한다.
- borderline case와 실패 케이스를 사람 검토까지 연결한다.
- 실패를 다음 수정 작업으로 바로 이어지게 만든다.
- onboarding 및 향후 feature 변화로 context가 늘어나도 prompt가 덜 흔들리게 만든다.

한 줄로 요약하면, PromptOps는 “좋은 프롬프트를 한 번 만드는 일”이 아니라 “프롬프트를 계속 안정적으로 개선하는 운영 체계”입니다.

## 범위

PromptOps가 담당하는 범위는 다음과 같습니다.

- prompt family registry
- prompt revision과 lifecycle metadata
- curated dataset 기반 experiment orchestration
- evaluator 결과 비교
- review queue와 feedback contract
- failure taxonomy
- backlog item 생성 규칙
- project-specific context normalization contract
- LangSmith 연동

## 비범위

현재 PromptOps가 직접 담당하지 않는 항목은 다음과 같습니다.

- 범용 standalone PromptOps 제품화
- prompt review 전용 커스텀 UI
- review 없는 자동 prompt rewrite
- 복잡한 score calibration rule engine
- 아직 검증되지 않은 multi-project 공통 추상화

## 핵심 원칙

### 1. Prompt는 더 큰 계약의 일부다

프롬프트는 텍스트만으로 관리하지 않습니다.

각 prompt family는 다음과 함께 관리되어야 합니다.

- output schema contract
- policy contract
- context normalization contract
- evaluator set
- review rubric

### 2. 작은 변경 단위로 개선한다

한 번에 큰 rewrite를 하지 않습니다.

기본 원칙은 다음과 같습니다.

- baseline을 기록한다.
- 작은 diff 하나를 적용한다.
- dataset 실험을 돌린다.
- 결과를 비교한다.
- 실패 케이스를 review로 넘긴다.
- 다음 수정 항목을 backlog로 만든다.

### 3. raw context를 바로 prompt에 넣지 않는다

prompt는 raw onboarding/profile/job dict를 직접 읽는 대신 정규화된 context를 읽어야 합니다.

이 원칙은 다음 문제를 줄입니다.

- upstream feature shape 변경
- field naming drift
- 누락 정보 처리의 일관성 부족
- 프롬프트 본문에 과도한 데이터 의존성 발생

### 4. 외부 backend는 adapter 뒤에 둔다

현재 PromptOps는 LangSmith를 backend로 사용하지만, core가 LangSmith API에 직접 종속되지는 않습니다.

dataset sync, experiment 실행, compare link, review queue 연동은 adapter 계층 뒤에서 처리합니다.

### 5. failure는 반드시 다음 액션으로 이어져야 한다

실패는 “틀렸다”로 끝나면 안 됩니다.

모든 실패는 가능한 한 다음 중 하나로 연결되어야 합니다.

- prompt wording gap
- policy gap
- context normalization gap
- dataset truth gap
- missing product feature

## 구조

```text
src/promptops/
  core/
  adapters/
  projects/
    ai_career_concierge/
```

### `src/promptops/core`

PromptOps의 공통 운영 개념과 로직을 둡니다.

대표 역할:

- prompt family / revision 모델
- experiment spec / summary 모델
- review item / feedback 모델
- failure taxonomy 모델
- backlog item 모델
- dataset sync와 experiment orchestration

이 계층은 나중에 별도 패키지로 분리될 가능성이 있는 공통 영역입니다.

### `src/promptops/adapters`

외부 backend 연결부를 둡니다.

현재 역할:

- LangSmith dataset sync
- LangSmith experiment 실행
- compare link 생성
- annotation queue 생성 및 run 연결

### `src/promptops/projects/ai_career_concierge`

이 저장소 전용 PromptOps 설정과 정책을 둡니다.

대표 역할:

- prompt family 등록
- normalized evaluation context 정의
- review rubric 정의
- feedback를 backlog로 바꾸는 규칙

이 계층은 도메인 의미가 강하므로 당분간 프로젝트 전용으로 유지합니다.

## 핵심 엔티티

### Prompt Family

논리적으로 하나의 프롬프트 계열을 의미합니다.

예:

- `job-evaluation`
- `memory-summary`

각 family는 다음 정보를 가집니다.

- 식별자
- 설명
- 현재 active stage
- metadata
- revision 목록

### Prompt Revision

하나의 구체적인 변경 버전입니다.

revision은 최소한 다음 정보를 가져야 합니다.

- revision id
- 어떤 family에 속하는지
- 어떤 stage에 속하는지
- 어떤 이유로 바뀌었는지

### Lifecycle Stage

현재 lifecycle stage는 다음 세 가지를 사용합니다.

- `candidate`
- `staging`
- `production`

의미는 다음과 같습니다.

- `candidate`: 실험과 검토 중인 버전
- `staging`: 비교적 안정적이지만 추가 확인이 가능한 버전
- `production`: 실제 기준 버전

### Experiment

experiment는 특정 prompt revision을 curated dataset에 대해 평가한 실행 단위입니다.

최소한 다음과 연결되어야 합니다.

- prompt family
- dataset
- evaluator bundle
- compare link
- experiment metadata

### Review Item

사람 또는 LLM judge가 검토할 개별 단위입니다.

review item은 다음 정보를 가집니다.

- 어떤 prompt family인지
- 어떤 experiment인지
- 어떤 run인지
- 어떤 이유로 review에 들어왔는지
- 현재 상태가 무엇인지

### Failure Record

실패를 구조적으로 기록한 객체입니다.

최소 정보:

- taxonomy key
- category
- 요약
- 근거

### Backlog Item

다음 iteration 후보 작업입니다.

최소 정보:

- item key
- category
- priority
- title
- action
- evidence

## PromptOps 운영 프로세스

PromptOps는 아래 순서로 운영합니다.

1. 대상 prompt family를 고른다.
2. baseline revision과 baseline experiment를 기록한다.
3. 작은 prompt diff 또는 context diff 하나를 만든다.
4. curated dataset으로 experiment를 실행한다.
5. baseline과 candidate를 compare한다.
6. evaluator miss와 borderline case를 추린다.
7. 필요한 case를 human review queue로 보낸다.
8. review 결과를 taxonomy와 backlog item으로 변환한다.
9. candidate를 유지, 수정, promote 중 하나로 결정한다.
10. iteration 산출물을 문서로 남긴다.

iteration 산출물은 `docs/promptops_iterations/` 아래에 기록합니다.

## Context Normalization 원칙

PromptOps에서 prompt는 raw 입력 대신 normalized context를 읽어야 합니다.

현재 job evaluation 기준 normalized context는 다음 성격을 가집니다.

- hard preferences
- soft preferences
- job evidence
- missingness

즉, prompt는 원본 onboarding payload의 shape에 직접 의존하지 않고 “평가에 필요한 의미 단위”에 의존해야 합니다.

## Review 운영 원칙

### Review mode

- `llm_judge`
- `human`

### Human review 대상

human review는 모든 케이스를 다루지 않습니다.

우선순위는 다음과 같습니다.

- borderline case
- evaluator miss가 있는 case
- 정책적으로 민감한 case

현재 기본 rule은 다음과 같습니다.

- `fit_score`가 `40`에서 `79` 사이
- 또는 `role_alignment = MEDIUM`
- 또는 tracked evaluator score 중 하나라도 `1.0` 미만

### Human rubric

현재 `job-evaluation` human rubric은 다음 항목을 사용합니다.

- `role_alignment`
- `must_have_coverage`
- `deal_breaker_handling`
- `transferable_skill_credit`
- `summary_usefulness`

### Review queue

현재 기본 human review queue는 다음과 같습니다.

- queue name: `job-evaluation-review`
- backend: LangSmith
- queue mode: `single`

## Failure Taxonomy 원칙

실패는 category와 taxonomy key로 분류합니다.

현재 category는 다음과 같습니다.

- `prompt`
- `context`
- `dataset`
- `policy`
- `feature`

현재 대표 taxonomy key는 다음과 같습니다.

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

이 taxonomy는 “문제가 어디 있는가”를 빠르게 분리하기 위한 운영 도구입니다.

## Backlog 운영 원칙

review나 experiment 결과는 backlog item으로 이어져야 합니다.

기본 priority 규칙은 다음과 같습니다.

- `policy` → `P0`
- `feature` → `P1`
- `prompt` → `P1`
- `context` → `P1`
- `dataset` → `P2`

일반적으로 다음 흐름을 따릅니다.

1. failure를 taxonomy로 분류한다.
2. category를 정한다.
3. evidence를 붙인다.
4. backlog item을 만든다.
5. 다음 iteration 후보로 등록한다.

## LangSmith 역할

현재 LangSmith는 PromptOps의 기본 backend입니다.

주요 역할:

- prompt lineage 저장
- dataset sync
- experiment 실행
- compare link 제공
- annotation queue 기반 human review
- machine / human feedback 저장

이 프로젝트는 현재 LangSmith를 적극 활용하지만, PromptOps core는 LangSmith와 직접 결합하지 않도록 유지해야 합니다.

## 분리 원칙

PromptOps는 현재 이 저장소 내부 모듈로 존재하지만, 나중에는 일부를 분리할 수 있어야 합니다.

분리 가능성이 높은 부분:

- core models
- registry interface
- experiment orchestration interface
- review item / feedback contract
- failure / backlog 기본 모델
- LangSmith adapter

당분간 프로젝트 전용으로 남겨둘 부분:

- fit score 정책 의미
- `job-evaluation` prompt 의미 체계
- job matching용 normalized context
- human review rubric
- feedback에서 backlog로 가는 domain-specific 규칙

즉, 운영 프레임은 공통화 가능하게 만들고, 평가 의미 체계는 프로젝트 전용으로 유지하는 것이 원칙입니다.

## 참고 문서

- 제품/기술 컨텍스트: [`CONTEXT.md`](./CONTEXT.md)
- 기술 설계: [`TRD.md`](./TRD.md)
- iteration 기록: `docs/promptops_iterations/`
