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
