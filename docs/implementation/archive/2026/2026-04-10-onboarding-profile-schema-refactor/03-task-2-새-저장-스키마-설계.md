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
