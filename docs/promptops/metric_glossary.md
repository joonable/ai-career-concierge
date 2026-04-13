# PromptOps 평가 지표 glossary

날짜: 2026-04-13 (Asia/Seoul)

이 문서는 `/internal/prompts` 운영 화면과 iteration 문서에서 보게 되는 PromptOps 지표를 사람이 바로 해석할 수 있게 정리한 기준서입니다.

목표는 다음과 같습니다.

- 운영자가 지표 이름만 보고도 무엇을 의미하는지 이해할 수 있게 한다.
- 점수 하나만 보지 않고, 어떤 종류의 실패인지 다음 행동까지 연결할 수 있게 한다.
- 한국어 채용 공고 기준으로 `job-evaluation` PromptOps를 해석하는 공통 언어를 만든다.

## 읽는 순서

PromptOps 운영자는 아래 순서로 해석합니다.

1. 현재 상태판의 `Pass Rate`, 최신 결정, latest summary를 본다.
2. 어떤 evaluator key가 실패했는지 확인한다.
3. 실패가 `prompt / policy / dataset / context / feature` 중 어디에 가까운지 판단한다.
4. 필요하면 iteration 문서와 review queue를 열어 실제 사례를 확인한다.

## 먼저 알아둘 기준

### 운영 점수와 evaluator 점수는 다르다

- `fit_score`는 공고 자체가 현재 단일 사용자 PoC에 얼마나 추천 가능한지를 뜻하는 운영 점수입니다.
- evaluator의 `score`는 각 규칙이 맞았는지 틀렸는지를 보는 검증 점수입니다.
- 즉, `fit_score`가 높아도 evaluator에서는 실패할 수 있고, 반대로 낮은 `fit_score`가 정책상 맞다면 evaluator에서는 성공할 수 있습니다.

### 현재 기본 추천 임계치는 80점이다

- `minimum_fit_score` 기본값은 `80`입니다.
- 운영상 `fit_score >= 80`이면 Slack 전달 후보로 간주합니다.
- 따라서 `classification_match`는 "추천할지 말지"를 80점 기준으로 맞게 판단했는지를 보는 지표입니다.

### 점수 해석은 정밀도 우선이다

- 이 제품은 recall보다 precision을 우선합니다.
- 경계 사례에서는 "조금 관련 있어 보인다"보다 "정말 추천해도 되는가"를 더 중요하게 봅니다.
- 인접 직무는 무조건 저점 처리하지 않지만, must-have 부족과 ownership 부족을 함께 보며 보수적으로 해석합니다.

## 핵심 운영 신호

### `fit_score`

- 의미: 현재 사용자에게 이 공고를 얼마나 추천할 수 있는지 나타내는 1~100 운영 점수
- source: 모델 출력 및 평가 결과
- 운영 해석:
  - `80~100`: 강한 추천
  - `60~79`: 검토 가능하지만 기본 알림 임계치 아래
  - `40~59`: 인접 직무 또는 탐색 가치가 있는 경계 사례
  - `1~39`: 비추천
- 주의점: `fit_score`는 단순 호감도가 아니라 역할 정렬, must-have, deal-breaker를 함께 반영한 전달 판단 점수다.

### `confidence`

- 의미: 모델이 현재 판단을 얼마나 명확한 근거로 내렸는지 나타내는 별도 축
- allowed values: `HIGH`, `MEDIUM`, `LOW`
- 운영 해석:
  - `HIGH`: 역할 불일치나 강한 적합이 비교적 분명함
  - `MEDIUM`: 경계 사례이거나 일부 근거가 불완전함
  - `LOW`: 정보 부족 또는 해석 불확실성이 큼
- 주의점: `confidence`는 `fit_score`의 다른 표현이 아니다.

### `Pass Rate`

- 의미: 실험 dataset 전체에서 evaluator를 모두 통과한 비율
- source: iteration 문서와 LangSmith experiment summary
- 운영 해석:
  - 높을수록 현재 prompt/policy/dataset 조합이 기대와 잘 맞음
  - 낮을수록 특정 rubric이나 policy 해석이 흔들리고 있을 가능성이 큼
- 주의점: 현재 dataset이 한국어 기준으로 엄격하게 잡혀 있으므로, 낮은 값은 prompt 실패뿐 아니라 gold expectation 불명확성도 시사할 수 있다.

## 평가 출력 신호

이 신호들은 모델이 직접 반환하거나 golden dataset이 기대하는 값입니다.

| 키 | 의미 | 주요 값 | 운영 해석 포인트 |
| --- | --- | --- | --- |
| `role_alignment` | 실제 책임 범위가 타깃 MLE 역할과 얼마나 직접 맞는지 | `HIGH`, `MEDIUM`, `LOW` | title보다 실제 책임과 ownership을 본다. |
| `must_have_coverage` | 사용자의 필수 조건이 얼마나 강하게 충족되는지 | `STRONG`, `PARTIAL`, `WEAK` | 일부 충족은 검토 가능일 수 있지만 보통 80+ 상한을 막는다. |
| `deal_breaker_severity` | 결격 사유가 얼마나 강하게 감지되는지 | `NONE`, `SOFT`, `HARD` | `HARD`면 높은 기술 적합도가 보여도 전달을 보수적으로 막아야 한다. |
| `transferable_skill_level` | 인접 직무라도 전이 가능한 역량이 얼마나 강한지 | `HIGH`, `MEDIUM`, `LOW` | 역할 불일치를 완전히 상쇄하지는 못하지만 borderline 판단에 중요하다. |
| `should_pass` | 현재 운영 기준상 추천 전달 대상인지 여부 | `true`, `false` | 기본적으로 `fit_score >= 80`과 연결된다. |

## Evaluator metric glossary

아래 지표는 `src/agent/evals/rule_based_evaluators.py` 기준의 현재 evaluator key입니다.

| 지표 키 | 무엇을 검증하나 | 실패가 시사하는 것 | 주로 연결되는 후속 분류 |
| --- | --- | --- | --- |
| `classification_match` | 전달 여부 판단이 gold expectation과 일치하는가 | 80점 임계치 해석 또는 전달 정책이 어긋남 | `policy.score_band_definition`, `prompt.role_alignment` |
| `fit_score_band` | `fit_score`가 기대 점수 구간 안에 들어오는가 | 점수 calibration이 흔들림 | `policy.score_band_definition` |
| `role_alignment_match` | 역할 정렬 레벨을 맞게 읽었는가 | 직접 역할과 인접 역할 구분이 흔들림 | `prompt.role_alignment` |
| `must_have_coverage_match` | must-have 충족도를 맞게 읽었는가 | 필수요건 부족을 약하게 보거나 과하게 봄 | `prompt.must_have_coverage` |
| `deal_breaker_severity_match` | deal-breaker 강도를 맞게 읽었는가 | 거절 사유 반영이 일관되지 않음 | `policy.deal_breaker_handling` |
| `transferable_skill_credit` | 인접 경험에 적절한 크레딧을 줬는가 | adjacent role을 과대/과소평가함 | `prompt.transferable_skill_credit` |
| `hard_reject_penalty` | hard reject 상황에서 점수를 충분히 눌렀는가 | role/deal-breaker가 강한데도 전달 점수가 높음 | `policy.deal_breaker_handling`, `policy.score_band_definition` |
| `summary_concise` | 요약이 짧고 읽기 쉬운가 | 사람 검토용 설명 품질이 약함 | `prompt.summary_usefulness` |
| `must_have_expectation` | 기대한 must-have 근거가 실제 출력에 포함됐는가 | 강점 추출 또는 근거 표현이 빈약함 | `prompt.must_have_coverage`, `context.normalization_gap` |
| `deal_breaker_expectation` | 기대한 deal-breaker 근거가 실제 출력에 포함됐는가 | 우려 신호 추출이 빠지거나 약함 | `policy.deal_breaker_handling`, `context.normalization_gap` |
| `strength_keywords_match` | 기대한 강점 키워드가 구조화 설명에 담겼는가 | 요약은 맞지만 운영자가 원하는 언어로 읽기 어려움 | `prompt.summary_usefulness`, `dataset.gold_expectation_gap` |
| `concern_keywords_match` | 기대한 우려 키워드가 구조화 설명에 담겼는가 | 위험 신호가 설명에 덜 드러남 | `prompt.summary_usefulness`, `dataset.gold_expectation_gap` |
| `confidence_alignment` | confidence 레벨이 기대와 일치하는가 | 모델 확신도 표현이 과감하거나 지나치게 보수적임 | `policy.score_band_definition`, `dataset.gold_expectation_gap` |

## 자주 보는 실패 패턴

### `fit_score_band`와 `classification_match`가 같이 깨질 때

- 의미: 단순 wording 문제가 아니라 전달 정책 자체가 흔들릴 가능성이 큽니다.
- 먼저 볼 것: `role_alignment`, `must_have_coverage`, `deal_breaker_severity`
- 주된 액션: prompt 수정 전에 `score band` 해석 기준과 gold expectation을 다시 확인합니다.

### `role_alignment_match`와 `transferable_skill_credit`가 같이 깨질 때

- 의미: 인접 직무를 읽는 방식이 불안정합니다.
- 대표 사례: ML platform, experimentation infra, data engineer for ML
- 주된 액션: `prompt.role_alignment`와 `prompt.transferable_skill_credit` backlog를 우선 봅니다.

### `strength_keywords_match`나 `concern_keywords_match`만 깨질 때

- 의미: 실제 판단보다 설명 언어가 evaluator 기대와 어긋났을 수 있습니다.
- 주의점: 이 경우는 prompt 실패가 아니라 gold keyword가 너무 좁게 잡혔을 가능성도 큽니다.
- 주된 액션: iteration 문서 reasoning snippet과 `dataset.gold_expectation_gap` 가능성을 함께 확인합니다.

### `confidence_alignment`만 자주 깨질 때

- 의미: 모델이 경계 사례에서 과도하게 자신감 있게 말하고 있을 가능성이 큽니다.
- 주된 액션: borderline 사례에서 `MEDIUM` confidence 기준을 문서와 prompt 양쪽에서 더 분명히 적습니다.

## failure taxonomy 연결 가이드

현재 PromptOps는 아래 taxonomy를 우선 사용합니다.

| taxonomy key | 언제 붙이나 | 예시 |
| --- | --- | --- |
| `prompt.role_alignment` | 직접/인접 역할 정렬 설명이 흔들릴 때 | 응용과학자, 데이터 엔지니어, MLOps 플랫폼 역할 해석 불안정 |
| `prompt.must_have_coverage` | must-have 부족이 점수나 설명에 약하게 반영될 때 | SQL, MLOps 부족인데 80+가 나오는 경우 |
| `prompt.transferable_skill_credit` | transferable skill을 과대/과소평가할 때 | 플랫폼 경험을 MLE 직접 경험처럼 읽는 경우 |
| `prompt.summary_usefulness` | 사람이 읽을 요약이 약하거나 장황할 때 | 강점/우려가 운영 언어로 보이지 않음 |
| `dataset.gold_expectation_gap` | gold expectation이 현재 정책보다 좁거나 모호할 때 | keyword mismatch만 반복적으로 발생 |
| `dataset.borderline_coverage_gap` | 경계 사례 데이터가 충분하지 않을 때 | adjacent role 유형이 반복되는데 예시가 부족 |
| `context.normalization_gap` | 입력 context에 안정 판단에 필요한 신호가 빠질 때 | ownership, 근무 형태, seniority 신호 누락 |
| `policy.deal_breaker_handling` | deal-breaker 규칙이 문서/프롬프트에서 불명확할 때 | onsite-only, contract-only 처리 흔들림 |
| `policy.score_band_definition` | 점수 구간 해석이 흔들릴 때 | 60~79와 80+ 경계가 일관되지 않음 |
| `feature.onboarding_signal_missing` | 제품이 아예 필요한 신호를 수집하지 않을 때 | 사용자 선호나 회피 조건이 입력에 없음 |

## 운영자가 바로 쓰는 판단 규칙

- `Pass Rate`가 낮을 때는 먼저 가장 많이 깨진 evaluator key 2~3개를 모아서 봅니다.
- `fit_score_band` 실패는 보통 prompt wording보다 policy/expectation 문제일 가능성이 큽니다.
- `strength_keywords_match` 단독 실패는 실제 추천 품질 하락과 동일하지 않을 수 있습니다.
- `role_alignment_match`와 `must_have_coverage_match`가 함께 깨지면 실제 추천 품질 리스크가 큰 편입니다.
- `deal_breaker_severity_match` 또는 `hard_reject_penalty` 실패는 Slack 전달 품질에 직접 영향이 있으므로 우선순위를 높게 둡니다.

## 함께 봐야 하는 문서

- 상위 기준서: [README.md](./README.md)
- 현재 상태판: [status.md](./status.md)
- 최신 iteration 예시: [iterations/iteration_002-final.md](./iterations/iteration_002-final.md)
- 제품 fit score 정책 배경: [CONTEXT.md](../CONTEXT.md)
