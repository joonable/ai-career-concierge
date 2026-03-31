# PromptOps

날짜: 2026-03-31 (Asia/Seoul)

## 문서 목적

이 문서는 AI Career Concierge에서 PromptOps를 운영하기 위한 기준서입니다.

이 문서의 목적은 다음 세 가지를 짧고 명확하게 유지하는 것입니다.

- PromptOps가 왜 필요한가
- 코드, LangSmith, 문서가 각각 무엇을 맡는가
- 실제 운영 흐름이 무엇인가

이 문서는 PromptOps 관련 문서들의 최상위 진입점입니다. 새 세션이나 새 협업자는 먼저 이 문서와 현재 상태판을 보면 됩니다.

문서 작성 원칙:

- PromptOps 관련 운영 문서는 한국어를 기본으로 작성합니다.
- 기술 용어나 외부 도구 이름처럼 영어가 중요한 경우에만 괄호로 병기합니다.
- 영어 문장만 단독으로 남기기보다 한국어 설명을 우선합니다.

## PromptOps의 정의

PromptOps는 프롬프트를 단순 문자열이 아니라 운영 대상로 관리하는 방식입니다.

이 저장소에서 PromptOps는 다음을 다룹니다.

- prompt family
- schema와 policy contract
- context normalization
- experiment와 compare
- LLM judge와 human review
- failure 분류와 다음 backlog

한 줄로 요약하면, PromptOps는 “프롬프트를 계속 안전하게 개선하기 위한 운영 체계”입니다.

## 목표

이 저장소의 PromptOps 목표는 다음과 같습니다.

- 프롬프트 변경을 작은 단위로 안전하게 진행한다.
- curated dataset으로 변경 효과를 측정한다.
- borderline / failure case를 사람 검토까지 연결한다.
- 실패를 다음 작업으로 바로 이어지게 만든다.
- context 변화가 생겨도 prompt가 덜 흔들리게 만든다.

## 범위

PromptOps가 직접 다루는 범위는 다음과 같습니다.

- prompt family registry
- runtime contract와 schema binding
- normalized context contract
- experiment orchestration
- review contract
- failure taxonomy
- backlog 생성 규칙의 최소 로직
- LangSmith adapter

## 비범위

다음은 현재 PromptOps의 직접 범위가 아닙니다.

- 범용 standalone PromptOps 제품화
- 커스텀 review UI 구현
- review 없는 자동 prompt rewrite
- 복잡한 점수 보정 엔진
- 장기 backlog 자체의 canonical 저장소 역할

## 핵심 원칙

### 1. Prompt는 계약의 일부다

prompt text만 따로 관리하지 않습니다.

각 prompt family는 최소한 아래와 함께 관리되어야 합니다.

- output schema contract
- policy contract
- context normalization contract
- evaluator set
- review rubric

### 2. 작은 변경만 한다

PromptOps의 기본 단위는 큰 rewrite가 아니라 작은 iteration입니다.

원칙:

- baseline을 기록한다.
- 작은 diff 하나를 적용한다.
- experiment를 돌린다.
- compare한다.
- review로 넘긴다.
- 다음 backlog를 만든다.

### 3. raw context를 직접 주입하지 않는다

prompt는 raw onboarding/profile/job payload가 아니라 normalized context를 읽어야 합니다.

이 원칙은 다음 문제를 줄입니다.

- 입력 shape 변경
- 누락 정보 처리 불일치
- 프롬프트 본문의 과도한 데이터 의존성

### 4. 외부 backend는 adapter 뒤에 둔다

현재 PromptOps는 LangSmith를 사용하지만, core가 LangSmith 자체에 직접 결합되지는 않습니다.

dataset sync, experiment, compare, review queue 연동은 adapter 계층을 통해 처리합니다.

### 5. failure는 반드시 다음 액션으로 이어진다

실패는 단순 관찰이 아니라 다음 작업으로 이어져야 합니다.

가능한 분류는 다음과 같습니다.

- prompt gap
- policy gap
- context gap
- dataset gap
- feature gap

## 역할 분담

### 코드가 맡는 것

코드는 runtime contract와 orchestration만 가집니다.

대표 항목:

- prompt family key와 identifier binding
- schema version과 structured output contract
- normalized context schema와 mapping
- experiment orchestration interface
- review payload shape
- failure taxonomy key
- backlog 생성 규칙의 최소 로직

### LangSmith가 맡는 것

LangSmith는 운영 truth를 맡습니다.

대표 항목:

- prompt version과 tag
- prompt commit lineage
- experiment run
- compare 결과
- annotation queue
- run-level machine / human feedback

운영 truth 원칙:

- 현재 어떤 prompt가 기준인지: LangSmith tag에서 본다.
- baseline과 candidate 비교: LangSmith compare에서 본다.
- review queue 상태: LangSmith annotation queue에서 본다.

### 문서가 맡는 것

문서는 사람이 읽는 운영 기록과 기준을 맡습니다.

대표 항목:

- PromptOps 운영 원칙
- iteration 요약
- 결과 해석
- decision 기록
- human-facing 상태 요약

### Notion이 맡는 것

Notion은 실제 후속 작업의 canonical 위치입니다.

대표 항목:

- backlog item
- priority
- owner
- 진행 상태

canonical backlog 원칙:

- 코드와 docs는 backlog 후보만 요약한다.
- 실제 backlog item의 정식 위치는 Notion이다.
- 현재 canonical backlog DB: [PromptOps Backlog](https://www.notion.so/c5fb7393ece54107b445e90bdabab642)

## 구조

```text
src/promptops/
  core/
  adapters/
  projects/
    ai_career_concierge/
```

### `src/promptops/core`

공통 운영 모델과 orchestration 로직을 둡니다.

### `src/promptops/adapters`

LangSmith 같은 외부 backend 연결부를 둡니다.

### `src/promptops/projects/ai_career_concierge`

이 저장소 전용 prompt family, normalized context, review rubric, backlog mapping 규칙을 둡니다.

## 실제 운영 흐름

PromptOps의 실제 운영 흐름은 아래와 같습니다.

1. 대상 prompt family를 정한다.
2. baseline을 기록한다.
3. 작은 prompt 또는 context diff를 만든다.
4. curated dataset으로 experiment를 실행한다.
5. baseline과 candidate를 compare한다.
6. borderline / failed case를 review queue로 보낸다.
7. review 결과를 해석한다.
8. failure를 backlog 후보로 바꾼다.
9. candidate 유지 / 승격 / 보류를 결정한다.
10. iteration 결과를 문서로 남긴다.

## Iteration 기록 규칙

iteration 운영 히스토리는 코드가 아니라 `docs/promptops_iterations/`에 남깁니다.

기본 원칙:

- 각 iteration은 하나의 baseline, 하나의 candidate, 하나의 decision을 중심으로 기록한다.
- compare 링크와 review queue는 LangSmith 기준으로 남긴다.
- backlog는 후보 요약만 문서에 남기고, canonical item은 Notion에서 관리한다.

각 iteration 문서에는 최소한 아래 정보가 있어야 합니다.

- prompt family
- baseline / candidate reference
- baseline vs candidate compare 링크
- 핵심 metric 변화
- human review queue 정보
- decision
- next backlog top 3

새 iteration을 만들 때는 [`docs/promptops_iterations/TEMPLATE.md`](./promptops_iterations/TEMPLATE.md)를 사용합니다.

## 협업용 운영 뷰

개발자와 비개발자는 같은 순서로 정보를 확인합니다.

1. [`promptops_status.md`](./promptops_status.md)
2. 최신 iteration 문서
3. LangSmith compare
4. LangSmith review queue
5. Notion backlog

웹에서는 `/internal/promptops` 라우트가 같은 상태를 내부 운영 패널 형태로 보여줍니다.

역할별 차이는 해석의 깊이이지, 출발 문서는 다르지 않습니다.

### 개발자가 주로 보는 것

- 현재 production / staging / candidate tag
- compare 결과와 evaluator 변화
- review queue 상태
- 다음 수정 후보 key

### PM / 운영자가 주로 보는 것

- 현재 운영 기준 prompt
- 최근 experiment 결과의 개선/하락 여부
- 이번 iteration 결론
- 다음 작업 우선순위

## 운영 문서 체계

PromptOps 관련 문서는 아래 네 축만 유지합니다.

- 상위 기준서: [`PROMPTOPS.md`](./PROMPTOPS.md)
- 현재 상태판: [`promptops_status.md`](./promptops_status.md)
- 실제 iteration 기록: `docs/promptops_iterations/`

문서 수를 늘리지 않기 위해, 세부 설계 메모나 migration 중간 판단은 장기 문서로 유지하지 않습니다.

## 분리 원칙

PromptOps는 지금 이 저장소 안에 있지만, 나중에 일부는 별도 패키지로 분리될 수 있어야 합니다.

분리 가능성이 높은 부분:

- core model
- registry interface
- experiment orchestration interface
- review / feedback contract
- failure / backlog 기본 모델
- LangSmith adapter

당분간 프로젝트 전용으로 남을 부분:

- fit score 정책 의미
- `job-evaluation` 도메인 의미 체계
- job matching용 normalized context
- review rubric
- domain-specific backlog mapping 규칙

## 참고 문서

- 제품/기술 컨텍스트: [`CONTEXT.md`](./CONTEXT.md)
- 기술 설계: [`TRD.md`](./TRD.md)
- 현재 상태판: [`promptops_status.md`](./promptops_status.md)
- iteration 기록: `docs/promptops_iterations/`
