# Onboarding Profile Schema Refactor

## 목적

새 온보딩 UI가 수집하는 정보를 현재 `profile_data.role`, `guidelines.must_haves`, `guidelines.deal_breakers`에 억지로 밀어 넣지 않고,
의미에 맞는 구조로 저장/해석/표시하기 위한 기준 문서다.

이 문서는 다음 두 가지를 정의한다.

1. 현재 계약과 새 온보딩 데이터의 차이
2. 새 저장 스키마 초안

## Task 1. 현재 계약과 새 온보딩 데이터 차이 정리

### 현재 온보딩 UI가 수집하는 값

현재 `/onboarding` UI는 아래 정보를 수집한다.

- 직무
  - 복수 선택 가능
  - 예: `ML Engineer`, `LLM Engineer`, `Data Scientist`
- 경력 레벨
  - 복수 선택 가능하지만 실제 의미상 단일 수준 선택에 가까움
  - 예: `junior`, `mid`, `senior`, `staff`
- 근무 형태
  - 복수 선택
  - 예: `remote`, `hybrid`, `onsite`
- 지역
  - 복수 선택
  - 예: `seoul`, `pangyo`, `bundang`, `gyeonggi`, `daejeon`, `busan`, `nationwide`, `global`
- 팀 맥락
  - 복수 선택
  - 예: `ai-first`, `product-team`, `platform-team`, `small-team`, `specialist-team`
- 중요 스킬
  - preset 복수 선택 + custom keyword
  - 예: `Python`, `SQL`, `PyTorch`, `RAG`
- 빠르게 제외할 조건
  - preset 복수 선택 + custom keyword
  - 예: `contract`, `research-heavy`, `no-llm`, `박사 학위 필수`
- 비교 선택
  - slider 기반 축별 값
  - 예: `delivery-vs-research = 1`
- 보조 메모
  - optional free text
- 최소 적합도 점수
  - integer

### 현재 API 계약이 이해하는 값

현재 백엔드 계약은 아래 구조를 기준으로 한다.

- `profile_data`
  - `role`
  - `years_of_experience`
  - `title_keywords`
- `guidelines`
  - `must_haves`
  - `deal_breakers`
- `notification_settings`
  - `minimum_fit_score`
  - `delivery_channel`

### 현재 UI 값이 기존 계약에 들어가는 방식

현재 구현에서는 새 온보딩 값이 아래처럼 flatten 되어 저장된다.

#### `profile_data`

- `selectedRoles` -> `profile_data.role`
  - 복수 선택을 `", "`로 join 한 문자열로 저장
- `selectedSeniority` -> `profile_data.years_of_experience`
  - 선택한 수준을 대표 연차 숫자로 매핑

#### `guidelines.must_haves`

아래 서로 다른 성격의 값이 모두 한 배열에 섞여 저장된다.

- 중요 스킬
  - 예: `Python`, `SQL`, `RAG`
- custom 스킬
  - 예: `Spark`, `LangChain`
- 근무 형태
  - 예: `근무 형태: 하이브리드`
- 지역
  - 예: `지역: 판교`
- 팀 맥락
  - 예: `팀 맥락: 프로덕트와 가까운 역할`
- 비교 선택
  - 예: `선호: 약하게 오른쪽 (모델 개발 중심 / 서비스 적용 중심)`
- 보조 메모
  - 예: `메모: B2B SaaS 경험 선호`

#### `guidelines.deal_breakers`

- preset 제외 조건
  - 예: `계약직 중심`, `LLM 업무가 전혀 없음`
- custom 제외 조건
  - 예: `박사 학위 필수`

### 현재 방식의 문제

- `must_haves`가 더 이상 must-have 의미를 가지지 않는다.
- evaluator가 스킬, 지역, 근무 형태, 팀 맥락, 비교 선택을 서로 다른 규칙으로 해석할 수 없다.
- dashboard가 사용자 설정을 설명할 때 의미 단위별로 묶어 보여주기 어렵다.
- 프론트가 저장 의미가 아니라 레거시 필드명에 맞춰 payload를 왜곡한다.
- 추후 rule filter에서 지역/근무 조건을 구조적으로 활용하기 어렵다.

### 값별 책임 분리

각 값은 아래 레이어에서 서로 다른 책임을 가진다.

| 수집 값 | 저장 스키마 | evaluator | dashboard |
| --- | --- | --- | --- |
| 직무 | 필요 | 필요 | 필요 |
| 경력 레벨 / 연차 | 필요 | 필요 | 필요 |
| 근무 형태 | 필요 | 필요 | 필요 |
| 지역 | 필요 | 필요 | 필요 |
| 팀 맥락 | 필요 | 필요 | 필요 |
| 중요 스킬 | 필요 | 필요 | 필요 |
| custom 스킬 | 필요 | 필요 | 필요 |
| 제외 조건 preset | 필요 | 필요 | 필요 |
| 제외 조건 custom | 필요 | 필요 | 필요 |
| 비교 선택 | 필요 | 필요 | 필요 |
| 보조 메모 | 필요 | 필요 | 필요 |
| 최소 적합도 점수 | 필요 | 필요 | 필요 |

### 레이어별 해석 원칙

#### 저장 스키마

- UI가 수집한 의미를 최대한 그대로 보존한다.
- 프롬프트나 dashboard 표시를 위해 의미를 섞지 않는다.
- preset 값은 안정적인 ID로 저장한다.
- custom 입력은 문자열로 저장한다.

#### evaluator

- 저장 스키마를 직접 읽지 않는다.
- normalized context builder가 아래처럼 변환한다.
  - role/years/title keywords
  - skill preferences
  - work preferences
  - exclusion signals
  - comparison tones
  - note

#### dashboard

- 저장 스키마를 직접 나열하지 않는다.
- presenter가 저장값을 사용자에게 읽기 쉬운 요약 카드/태그/문장으로 변환한다.

## Task 2. 새 저장 스키마 설계

### 설계 원칙

- `profile_data`는 사용자의 정체성(identity)와 기본 타겟 정보를 저장한다.
- `preferences`는 추천 해석에 필요한 온보딩 선호를 저장한다.
- `notification_settings`는 알림과 임계값 설정만 저장한다.
- 저장은 가능하면 ID 기반으로 하고, UI 표시용 label은 프론트/백엔드 mapping layer에서 관리한다.
- free text는 오직 custom keyword와 note에만 남긴다.

### 제안 스키마 초안

```json
{
  "profile_data": {
    "roles": ["ml-engineer", "llm-engineer"],
    "primary_role": "ml-engineer",
    "years_of_experience": 6,
    "seniority": "senior",
    "title_keywords": ["ml engineer", "llm engineer"]
  },
  "preferences": {
    "work_modes": ["hybrid", "onsite"],
    "locations": ["seoul", "pangyo", "bundang", "gyeonggi"],
    "team_contexts": ["ai-first", "product-team"],
    "skills": {
      "preset": ["python", "sql", "pytorch", "rag"],
      "custom": ["Spark"]
    },
    "exclusions": {
      "preset": ["contract", "research-heavy", "no-llm"],
      "custom": ["박사 학위 필수"]
    },
    "comparisons": {
      "delivery-vs-research": 1,
      "llm-vs-classic": -1,
      "ownership-shape": 1
    },
    "note": null
  },
  "notification_settings": {
    "minimum_fit_score": 80,
    "delivery_channel": "slack"
  }
}
```

### 필드 책임 정의

#### `profile_data`

- `roles`
  - 사용자가 보고 싶은 직무의 전체 선택 목록
  - 추천/대시보드/후속 title keyword 파생의 기준
- `primary_role`
  - 대표 직무 1개
  - rule filter와 dashboard headline에서 우선 사용
- `years_of_experience`
  - 수치 기반 경력
  - rule filter와 evaluator 입력에 사용
- `seniority`
  - UI 복원 및 표시용 수준 값
  - `years_of_experience`와 함께 저장
- `title_keywords`
  - role 기반 파생 + 필요 시 향후 사용자 커스텀 확장 가능
  - rule filter title matching에 사용

#### `preferences`

- `work_modes`
  - 근무 형태 선호
  - rule filter, evaluator, dashboard 모두 사용
- `locations`
  - 지역 선호
  - rule filter, evaluator, dashboard 모두 사용
- `team_contexts`
  - 팀 구조/역할 성격 선호
  - evaluator와 dashboard에서 주로 사용
- `skills.preset`
  - 정규화 가능한 주요 스킬 ID
  - evaluator, dashboard, future filtering에 사용
- `skills.custom`
  - 자유 입력 스킬
  - evaluator와 dashboard에서 사용
- `exclusions.preset`
  - 정규화 가능한 제외 조건 ID
  - evaluator와 rule filter에서 사용
- `exclusions.custom`
  - 자유 입력 제외 조건
  - evaluator에서 주로 사용
- `comparisons`
  - slider 축별 점수
  - evaluator prompt tone shaping과 dashboard 요약에 사용
- `note`
  - 구조화되지 않는 마지막 보조 맥락
  - evaluator와 dashboard에서 사용

#### `notification_settings`

- `minimum_fit_score`
  - Slack 추천 임계값과 dashboard 기준선
- `delivery_channel`
  - 현재는 `slack` 고정

### ID 기반 저장 vs label 기반 저장

결론:

- preset 옵션은 `ID 기반 저장`
- custom 입력과 note는 `label/string 저장`

#### ID 기반 저장이 더 적합한 이유

- UI 문구가 바뀌어도 저장 데이터는 안정적이다.
- 한글/영문 label이 바뀌어도 evaluator와 dashboard mapping이 깨지지 않는다.
- 비교 선택, 팀 맥락, 제외 조건처럼 문구가 자주 다듬어질 수 있는 항목에 유리하다.
- rule filter와 prompt builder에서 분기 로직을 쓰기 쉽다.

#### label 기반 저장이 필요한 경우

- custom skill
- custom exclusion
- note
- title keyword처럼 사용자 또는 시스템이 실제 텍스트로 다뤄야 하는 값

### enum/ID 후보

#### roles

- `ml-engineer`
- `llm-engineer`
- `data-scientist`
- `mlops`
- `backend-ai`

#### seniority

- `junior`
- `mid`
- `senior`
- `staff`

#### work_modes

- `remote`
- `hybrid`
- `onsite`

#### locations

- `seoul`
- `pangyo`
- `bundang`
- `gyeonggi`
- `daejeon`
- `busan`
- `nationwide`
- `global`

#### team_contexts

- `ai-first`
- `product-team`
- `platform-team`
- `small-team`
- `specialist-team`

#### skills.preset

- `python`
- `sql`
- `pytorch`
- `tensorflow`
- `llm`
- `rag`
- `evaluation`
- `airflow`
- `mlops`
- `aws`
- `backend`
- `analytics`

#### exclusions.preset

- `contract`
- `internship`
- `onsite-only`
- `research-heavy`
- `no-llm`
- `korean-required`
- `visa-none`

#### comparisons

- `delivery-vs-research`
- `company-shape`
- `llm-vs-classic`
- `ownership-shape`
- `speed-vs-process`
- `build-vs-operate`

값은 `-2, -1, 0, 1, 2` 정수로 저장한다.

### 저장 스키마에서 의도적으로 하지 않는 것

- `must_haves`, `deal_breakers` 같은 evaluator 중심 레거시 명칭을 1급 저장 구조로 두지 않는다.
- dashboard 표시 문구를 저장하지 않는다.
- comparison을 자연어 문자열로 저장하지 않는다.
- 근무 형태, 지역, 팀 맥락을 하나의 문자열 리스트에 섞지 않는다.

## 후속 구현 메모

다음 단계 구현 순서는 아래를 권장한다.

1. 백엔드 schema에 `preferences` 추가
2. 기존 `guidelines`는 호환용으로 유지
3. normalized context builder에서 새 구조 우선 사용
4. dashboard presenter에서 새 구조 우선 사용
5. 프론트 submit/restore를 새 스키마로 교체
6. 최종적으로 레거시 `must_haves`, `deal_breakers` 제거 여부 판단
