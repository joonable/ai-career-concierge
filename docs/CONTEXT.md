# 프로젝트 컨텍스트 (Project Context)

## 목적 (Purpose)

AI Career Concierge는 채용 공고의 노이즈를 줄이고 각 사용자에게 적합도가 높은 역할만 큐레이션하는 AI 기반 채용 매칭 시스템입니다. 현재 단계는 제품을 빌드하는 개발자이자 5-6년 차 MLE인 단일 기본 사용자 프로필에 중점을 둔 PoC(개념 증명)입니다.

## 현재 제품 범위 (Current Product Scope)

PoC는 핵심 루프를 엔드투엔드(end-to-end)로 지원해야 합니다:

1. 사용자가 로그인하여 프로필, 필수 조건(must-haves) 및 결격 사유(deal-breakers)를 설정합니다.
2. 시스템이 대상 플랫폼에서 새로운 채용 공고를 수집(ingest)합니다.
3. 공고는 2단계 평가 파이프라인을 거칩니다:
   - 규칙 기반 필터링(rule-based filtering)을 먼저 수행합니다.
   - 규칙을 통과한 공고에 대해서만 LLM 기반 심층 평가(LLM-based deep evaluation)를 수행합니다.
4. 높은 점수를 받은 공고는 Slack을 통해 전달됩니다.
5. 사용자는 좋아요/싫어요(like/dislike) 피드백을 남깁니다.
6. 최근의 부정적인 피드백은 향후 평가에서 단기 기억(short-term memory)으로 재사용됩니다.

## 제품 우선순위 (Product Priorities)

- 재현율(recall)보다 추천 정밀도(precision) 최적화.
- 모델 호출 전 공격적인 필터링으로 LLM 비용 최소화.
- 광범위한 SaaS 규모를 설계하기 전에 한 명의 사용자에 대해 첫 번째 버전을 안정적으로 운영.
- 피드백을 통해 다음 날의 추천이 실질적으로 개선되도록 구성.

## 확정된 기술 스택 (Confirmed Tech Stack)

- 프론트엔드: Next.js
- 백엔드 API: FastAPI
- 에이전트 오케스트레이션: LangGraph
- LLM 제공자: 구조화된 JSON 출력이 가능한 Google Gemini Flash
- 스크래핑: Python async 실행의 Playwright
- 데이터베이스 및 인증: Google OAuth 기반 Supabase PostgreSQL
- ORM: SQLModel
- 스케줄러: GitHub Actions cron 트리거
- 추적(Tracing): LangSmith

## 현재 구현 구조 (Current Implementation Layout)

저장소는 Python 백엔드를 `src/*` 레이아웃에 유지하고 프론트엔드를 `apps/web`에 분리합니다.

- `apps/web`
  - Next.js App Router 프론트엔드
  - `src/app`은 `/login`, `/auth/callback`, `/onboarding`, `/dashboard`, `/internal`, `/internal/prompts`와 같은 라우트 진입점을 포함
  - `src/components`는 인증, 온보딩, 대시보드 컴포넌트와 같은 페이지 관련 UI를 포함
  - `src/lib`은 Supabase 인증 헬퍼, API 클라이언트 코드, 프론트엔드 런타임 어댑터를 포함
- `src/api`
  - FastAPI 라우트, 스키마, 의존성(dependencies), 가벼운 애플리케이션 서비스
  - 인증, 프로필, 대시보드, 피드백 및 파이프라인 런타임은 Supabase Auth와 Supabase Data API를 사용
  - 기본 파이프라인 런타임은 Gemini structured-output evaluator를 사용하고, 테스트는 mock evaluator를 주입
- `src/agent`
  - LangGraph 워크플로우, 노드 구현, 프롬프트, 타입이 지정된 파이프라인 상태
- `src/promptops`
  - 프롬프트 실험, 리뷰, iteration 기록을 위한 PromptOps 스캐폴드
  - 현재는 이 저장소 내부 모듈로 시작하지만, core/adapters/project bindings 경계를 유지해 향후 분리를 염두에 둠
- `src/scraper`
  - 기본 스크래퍼 인터페이스, 노멀라이저(normalizer), 소스 레지스트리, 소스별 스크래퍼
  - 기본 런타임은 인크루트(Incruit) 실스크래퍼를 사용하고, 테스트는 fixture/mock scraper를 병행
- `src/db`
  - 레거시 SQLModel 모델, 저장소 기록 및 PoC 전환 기간 동안 유지되는 스키마 참조
- `src/common`
  - 타입이 지정된 구성(config), 로깅, 원격 측정(telemetry), id 및 공유 오류
- `tests`
  - 단위(unit), 통합(integration), 계약(contract) 및 복원력(resilience) 테스트
- `docs`
  - 제품/기술 문서와 함께 `/internal` 운영 허브가 읽는 canonical 운영 문서를 포함
  - 최상위에는 핵심 제품 문서만 두고, 운영 문서는 `docs/internal/`, PromptOps 문서는 `docs/promptops/`, 구현 메모는 `docs/implementation/`에 정리
  - 최소 운영 문서는 `docs/internal/status.md`, `docs/internal/operations_panel.md`, `docs/internal/agent_workboard.md`를 유지

## 핵심 비즈니스 로직 (Core Business Logic)

### 1단계: 규칙 기반 필터 (Stage 1: Rule-Based Filter)

이 단계는 LLM을 호출하기 전에 실행되어야 합니다.

- 이미 평가된 공고를 제외합니다.
- 공고 직함(job title)의 관련성으로 필터링합니다.
- 경력/직급(experience/seniority)의 적합성으로 필터링합니다.

이곳에서 거부된 직무는 `RULE_REJECTED` 상태로 저장되어야 합니다.

### 2단계: LLM 심층 평가 (Stage 2: LLM Deep Evaluation)

이 단계는 규칙 필터링을 통과한 공고에 대해서만 실행됩니다.

- 문맥 내의 결격 사유(deal-breakers)를 분석합니다.
- 필수 조건(must-haves)이 충족되는지 추론합니다.
- 1부터 100까지의 적합도(fit score)를 부여합니다.
- 약 2줄 정도의 짧은 추천 이유(reasoning)를 생성합니다.

여기서 완료된 공고는 `LLM_EVALUATED` 상태로 저장되어야 합니다.

### 적합도 점수 정책 (Fit Score Policy)

`fit_score`는 단순한 "좋아 보임" 점수가 아니라, 현재 PoC의 단일 사용자에게 실제로 추천할 만한지에 대한 운영 점수입니다. 이 점수는 재현율보다 정밀도를 우선해야 하며, 특히 애매한 인접 직무는 설명 가능한 기준으로 일관되게 다뤄야 합니다.

기본 점수 밴드 정의:

- `80~100`: 강한 추천
  - 목표 직무와 역할 정렬(role alignment)이 높고, 핵심 must-have 대부분이 충족되며, 뚜렷한 deal-breaker가 없어야 합니다.
- `60~79`: 검토 가능
  - 전반적으로 관련성이 높지만 일부 must-have 공백, 소유권 불명확성, 경계 조건이 남아 있는 경우입니다.
- `40~59`: 인접 직무 또는 전환 가능성
  - 직접적인 타깃 역할은 아니지만 transferable skill이 분명하고, 사용자 관점에서 탐색 가치는 있는 경우입니다.
- `1~39`: 비추천
  - 핵심 역할 불일치가 크거나, must-have 결손이 심하거나, 추천을 보수적으로 막아야 할 사유가 있는 경우입니다.

인접 직무(adjacent role) 정책:

- 직무명이 다르더라도 실제 업무가 MLE 역할과 충분히 겹치면 자동 저점 처리하지 않습니다.
- 다만 인접 직무는 "관련 있음"만으로 고득점을 주지 않고, 실제 역할 정렬과 책임 범위를 함께 봐야 합니다.
- 예를 들어 ML platform, backend serving, experimentation infra, data engineer for ML 같은 역할은 transferable skill이 강하면 `40~59` 또는 `60~79`까지 열어둘 수 있습니다.
- 반대로 타이틀은 ML과 가까워 보여도 실제 책임이 모델링, 서빙, 실험, 운영 중 핵심 축과 멀면 보수적으로 낮춰야 합니다.

must-have 부족 페널티 정책:

- must-have는 있으면 가산점이 아니라, 없으면 감점 또는 상한 제한을 만드는 핵심 조건으로 해석합니다.
- 핵심 must-have 대부분이 충족되면 `80+` 후보가 될 수 있습니다.
- 일부만 충족하는 경우에는 `60~79` 또는 `40~59`로 제한하는 것이 기본입니다.
- 타깃 역할의 핵심 축이 빠져 있으면 transferable skill이 있더라도 `80+`로 올리지 않습니다.
- must-have 부족은 단순 키워드 누락이 아니라 실제 책임, 소유권, 운영 경험 부족까지 포함해 판단합니다.

deal-breaker 정책:

- 명시적 deal-breaker가 감지되면 추천 여부를 보수적으로 판단합니다.
- hard deal-breaker가 있으면 높은 기술 적합도가 보여도 강한 추천으로 올리지 않습니다.
- deal-breaker는 점수만 낮추는 신호가 아니라, 실제 전달 여부와 reviewer 주의도를 함께 높이는 신호입니다.
- 운영상 명확한 결격 사유가 있으면 `should_pass`는 false가 되어야 하며, 필요하면 점수는 중간대에 머물더라도 추천은 막을 수 있습니다.

transferable skill 정책:

- transferable skill은 역할 불일치를 완전히 상쇄하지는 않지만, 인접 직무를 `1~39`에서 `40~59` 이상으로 끌어올릴 수 있는 근거입니다.
- transferable skill을 인정하려면 사용자의 핵심 강점이 실제 업무 책임과 연결되어 있어야 합니다.
- 단순 기술 스택 일부 중복만으로는 부족하며, Python/SQL/infra 경험이 실제 ML platform, serving, experimentation, data workflow ownership으로 이어지는지 봐야 합니다.
- 역할 정렬이 중간 수준이고 transferable skill이 강하면 최소한 "탐색 가치가 있는 인접 직무"로 평가할 수 있습니다.

confidence 정책:

- `confidence`는 점수 자체와 동일한 개념이 아니며, 모델이 현재 판단을 얼마나 명확한 근거로 내렸는지 나타내는 별도 축입니다.
- 높은 점수라도 근거가 불완전하거나 책임 범위가 모호하면 `MEDIUM` 또는 `LOW` confidence가 가능해야 합니다.
- 낮은 점수라도 deal-breaker나 역할 불일치가 명확하면 `HIGH` confidence가 가능해야 합니다.
- 따라서 `confidence`는 `fit_score`에 종속되지 않고, 점수 이유의 명확성과 정보 충분성을 반영해야 합니다.

운영 해석 가이드:

- `80+`는 Slack 추천 대상으로 간주하는 기본 후보입니다.
- `60~79`는 저장 및 검토 가치는 있지만, 현재 PoC 기본 알림 임계치보다 낮을 수 있습니다.
- `40~59`는 향후 calibration과 dataset 확장을 위한 중요한 borderline 관찰 구간입니다.
- borderline 사례에서는 점수 숫자 하나보다 역할 정렬, must-have 결손, transferable skill, deal-breaker 해석이 일관되게 유지되는지가 더 중요합니다.

### 피드백 루프 (Feedback Loop)

- 사용자는 추천을 `LIKE`, `DISLIKE`, `LATER`로 표시할 수 있습니다.
- `DISLIKE`는 거부 이유를 함께 저장할 수 있어야 합니다.
- 최근에 누적된 부정적인 피드백을 요약하여 향후 평가에 단기 기억으로 주입해야 합니다.

## 핵심 데이터 모델 (Core Data Model)

### 사용자 (User)

- 식별: `id`, `oauth_id`, `email`
- JSONB 형식의 프로필 데이터: 역할(role), 경력 연차, 기술 스택 등
- JSONB 형식의 가이드라인: 필수 조건(must-haves) 및 결격 사유(deal-breakers)

### 채용 공고 (Job)

- 식별: `id`, `platform`, `external_job_id`
- 중복 수집을 방지하기 위해 `external_job_id`로 소스별 고유성을 강제해야 합니다.
- 주요 필드: `title`, `company`, `jd_raw_text`, `url`

### 평가 (Evaluation)

- `user_id`와 `job_id`를 연결합니다.
- 수명 주기 상태:
  - `PENDING`
  - `RULE_REJECTED`
  - `LLM_EVALUATED`
- 주요 필드: `fit_score`, `reasoning`, `user_feedback`

### 시스템 로그 (System_Log)

- 파이프라인 실패, 스크래핑 오류 및 눈에 띄는 시스템 이벤트를 저장합니다.

## LangGraph 워크플로우 계약 (LangGraph Workflow Contract)

파이프라인은 다음 공유 상태를 가지는 LangGraph `StateGraph`로 모델링되어야 합니다:

- `current_jobs`: 수집된 채용 공고 대기열
- `user_context`: DB에서 불러온 프로필 및 가이드라인 데이터
- `recent_memory`: 요약된 최근의 싫어요 피드백
- `evaluation_results`: 최종 평가 출력

예상 노드 흐름:

1. `IngestNode`
2. `RuleFilterNode`
3. `LLMEvalNode`
4. `DeliverNode`

## 외부 인터페이스 (External Interfaces)

### 필수 API 엔드포인트 (Required API Endpoints)

- `POST /api/v1/pipeline/trigger`
  - 스케줄에 따라 GitHub Actions가 호출합니다.
  - 내부 `X-API-Key`를 검증해야 합니다.
- `POST /api/v1/slack/interactive-webhook`
  - Slack 버튼 동작을 수신합니다.
  - 평가 피드백 상태를 업데이트합니다.
- `GET /api/v1/users/me/dashboard`
  - 대시보드를 위한 개인화된 추천 데이터를 반환합니다.
  - 각 추천 항목에는 대시보드 필터/정렬을 지원하기 위한 `created_at`, `updated_at`, 제외 사유 표시를 위한 `rule_rejection_reason`, 상세 패널 구성을 위한 `jd_raw_text`, 경력 범위, `source_metadata`가 포함되어야 합니다.
  - 상세 패널은 추가로 `decision_summary`, `match_highlights`, `risk_highlights`, `confidence_level`, `rule_match_reasons`, `rule_rejection_details`, `responsibilities`, `requirements`, `preferred_requirements`, `location`, `employment_type`를 내려주며, 이 필드들은 현재 DB 저장값과 사용자 프로필을 바탕으로 백엔드에서 구조화해 응답합니다.
- `GET /api/v1/users/me/promptops-status`
  - 내부 PromptOps 운영 패널을 위한 수동 스냅샷 응답을 반환합니다.
  - 응답에는 production/staging/candidate prompt 식별자, latest decision, LangSmith compare / review queue 링크, Notion backlog 링크, 최신 iteration 요약이 포함됩니다.
  - 접근은 `PROMPTOPS_ADMIN_EMAILS` allowlist에 들어 있는 사용자 이메일로 제한됩니다.

## 운영 패널 문서 계약 (Operations Panel Document Contract)

- `/internal` 운영 허브는 runtime snapshot만이 아니라 docs 기반 운영 문서를 적극적으로 읽는 내부 패널이어야 합니다.
- 운영 패널은 최소한 다음 문서를 노출 대상으로 다뤄야 합니다:
  - `AGENTS.md`
  - `docs/CONTEXT.md`
  - `docs/TRD.md`
  - `docs/PRD.md`
  - `docs/internal/operations_panel.md`
  - `docs/internal/agent_workboard.md`
- 운영 패널은 문서 링크 나열에 그치지 않고, 어떤 문서가 source of truth인지와 마지막 업데이트 맥락을 함께 보여줘야 합니다.
- 운영 패널이 문서 편집 기능을 제공하는 경우, 최소한 운영 문서와 작업 보드 업데이트가 UI에서 가능해야 합니다.
- `docs/internal/agent_workboard.md`는 최근 완료 작업, 현재 작업 상태, 다음 action, backlog, UI 확인 경로를 담는 canonical workboard로 유지합니다.
- 에이전트가 의미 있는 작업을 마쳤다면 가능할 때마다 `docs/internal/agent_workboard.md`를 갱신해 운영 패널에서 바로 확인할 수 있게 해야 합니다.

## PromptOps 운영 초안

- PromptOps는 prompt 변경을 텍스트 수정이 아니라 실험 가능한 운영 루프로 다루기 위한 내부 모듈입니다.
- 1차 목표는 prompt family registry, experiment orchestration, evaluator/review 연결, iteration 기록의 경계를 코드와 문서로 고정하는 것입니다.
- LangSmith는 초기 PromptOps backend로 사용하되, 구현은 `src/promptops/adapters` 경계 뒤에 둡니다.
- 이 저장소의 job-matching 정책과 dataset/evaluator 의미는 `src/promptops/projects/ai_career_concierge`에 둬서, 향후 공통 PromptOps core 분리가 가능하도록 설계합니다.
- 내부 운영 가시성을 위해 `/internal` 운영 허브는 docs 기반 상태 요약, 작업 보드, 핵심 문서 레지스트리, PromptOps 스냅샷을 함께 보여주고, `/internal/prompts` 페이지는 LangSmith/Notion을 실시간 조회하지 않고 백엔드가 제공하는 PromptOps 상태 스냅샷을 렌더링합니다.

## 대시보드 상세 데이터 책임 분리

- DB 원본:
  - `title`, `company`, `url`, `platform`, `jd_raw_text`, `min_years_experience`, `max_years_experience`, `source_metadata`
  - `status`, `fit_score`, `reasoning`, `rule_rejection_reason`, `user_feedback`, `feedback_reason`, `created_at`, `updated_at`
- 규칙 엔진 결과:
  - `status=RULE_REJECTED`
  - `rule_rejection_reason`
  - `rule_match_reasons`, `rule_rejection_details`의 기반 판단
- LLM 생성:
  - `fit_score`
  - `reasoning`
- 백엔드 파생/구조화:
  - `decision_summary`
  - `match_highlights`
  - `risk_highlights`
  - `confidence_level`
  - `responsibilities`
  - `requirements`
  - `preferred_requirements`
  - `location`
  - `employment_type`
- 프론트 가공:
  - 상태/피드백 라벨 번역
  - 상대 시각 표기
  - 필터/정렬/검색에 따른 일시적 목록 상태

## 저장 대상과 비저장 대상

- 저장 대상:
  - 평가 상태, 점수, reasoning, 규칙 제외 사유
  - 사용자 피드백 상태와 피드백 메모
  - 공고 원문과 메타데이터
- 현재 비저장 대상:
  - 상세 패널 표시용 구조화 요약 필드(`decision_summary`, `match_highlights`, `risk_highlights`, `confidence_level`, `rule_match_reasons`, `rule_rejection_details`, `responsibilities`, `requirements`, `preferred_requirements`, `location`, `employment_type`)
  - 이 값들은 대시보드 응답 시점에 백엔드가 계산합니다.

### PoC 루프를 위해 추가된 스캐폴드 엔드포인트 (Scaffold Endpoints Added For The PoC Loop)

- `GET /api/v1/users/me/profile`
  - 정규화된 중첩 형태의 현재 사용자 프로필 및 알림 설정을 반환합니다.
- `PUT /api/v1/users/me/profile`
  - 프로필 데이터, 가이드라인 및 알림 설정을 업데이트합니다.
  - 역할, 연차, 필수 조건, 결격 사유, 최소 적합도 점수 등의 온보딩 필드를 허용합니다.
  - 역할이 생략된 경우 `role`에서 `profile_data.title_keywords`를 파생시키고, 알림 설정(`notification_settings.delivery_channel`)의 기본값을 `slack`으로 지정합니다.
- `POST /api/v1/evaluations/{evaluation_id}/feedback`
  - 대시보드 흐름에서 좋아요 또는 싫어요 피드백을 저장합니다.

### 현재 인증 계약 (Current Auth Contract)

- 웹 로그인 흐름은 `/login -> Google OAuth -> /auth/callback -> /dashboard` 입니다.
- 대시보드가 첫 번째 랜딩 페이지가 되며 온보딩이 아직 필요한지 여부를 나타냅니다.
- 웹 로그인은 Supabase Google OAuth를 사용하고 App Router SSR 쿠키 패턴으로 결과 세션을 저장합니다.
- `/onboarding` 및 `/dashboard`와 같이 보호된 웹 라우트에는 유효한 Supabase 세션이 필요합니다.
- 백엔드 사용자 엔드포인트에는 `Authorization: Bearer <Supabase access token>`이 필요합니다.
- 백엔드 인증은 프로젝트 JWKS에 대해 Supabase JWT를 확인하고 `sub` 및 `email`을 추출합니다.
- 백엔드 인증 관련 라우트와 파이프라인 영속성은 현재 `SUPABASE_SERVICE_ROLE_KEY`를 사용해 Supabase Data API를 사용합니다.

## 완료 조건 (Definition Of Done)

- 코드, 자동화된 테스트, 그리고 영향을 받는 문서 또는 설정 참조가 함께 업데이트될 때까지 기능은 완료된 것이 아닙니다.
- 동작이 변경되는 경우 같은 전송(delivery) 과정의 일환으로 로깅 및 오류 처리를 같이 검토해야 합니다.
- 구현만 된 작업은 완료된 것으로 간주하지 않습니다.

## 마이그레이션 가드레일 (Migration Guardrails)

- 스키마 변경을 계약 변경으로 취급하세요.
- 데이터베이스 스키마, 애플리케이션 모델, 수명 주기 enum, 그리고 영향을 받는 문서나 테스트를 동기화하여 유지하세요.
- 의미 있는 스키마 변경에는 마이그레이션 경로와 롤백 또는 호환성에 대한 고려 사항이 포함되어야 합니다.

## API 변경 가드레일 (API Change Guardrails)

- 요청 및 응답 스키마, 인증 동작, 웹훅 페이로드, 상태 enum을 안정적인 계약으로 취급하세요.
- API 계약이 변경되면 동일한 변경사항 내에 문서와 자동화된 테스트를 업데이트하세요.
- 변경 내용을 확정하기 전에 대시보드, Slack 흐름, 예약된 파이프라인 트리거에 미치는 하위 영향을 확인하세요.

## 전송 요구 사항 (Delivery Requirements)

- 주 알림 채널은 Slack입니다.
- Slack 메시지에는 다음이 포함되어야 합니다:
  - 공고 직함 (job title)
  - 회사 이름 (company name)
  - 적합도 점수 (fit score)
  - 짧은 추천 이유 (short reasoning)
  - 웹 대시보드로 통하는 딥 링크 (deep link to the web dashboard)

## 안정성 규칙 (Reliability Rules)

- 한 플랫폼에서의 스크래핑 실패가 전체 파이프라인을 중단시켜서는 안 됩니다.
- 실패한 플랫폼은 건너뛰고 기록해야 합니다.
- 운영 실패는 `System_Log`에 저장되어야 합니다.
- 중요한 실패는 `#system-alerts`와 같은 관리자 Slack 채널에 보고할 수 있어야 합니다.

## 옵저버빌리티(관측성) 가드레일 (Observability Guardrails)

- 각 파이프라인 실행은 `run_id` 또는 `trace_id`로 추적할 수 있어야 합니다.
- 중요한 로그는 `user_id`, `job_id`, `platform`, `status`, `error_type`의 관련 부분 집합을 캡처해야 합니다.
- 스크래퍼 실패, 평가 상태 전환, LLM 호출, Slack 전송, 웹훅 동작은 시크릿이나 불필요한 PII를 노출하지 않고 관찰할 수 있어야 합니다.
- 현재 구현은 `LANGSMITH_API_KEY`가 설정된 경우 파이프라인 실행 단위 root trace와 Gemini 평가 단위 child trace를 LangSmith에 기록합니다.
- `LANGSMITH_API_KEY`가 비어 있으면 LangSmith tracing은 비활성화되며, 기존 구조화 로그와 `System_Log` 기록만 유지됩니다.
- 평가 프롬프트는 `LANGSMITH_EVAL_PROMPT_IDENTIFIER`, `LANGSMITH_MEMORY_PROMPT_IDENTIFIER`로 Prompt Hub 태그 참조(`job-evaluation:staging`, `memory-summary:staging`)를 우선 사용하며, trace에는 요청한 태그와 실제 commit hash를 함께 남깁니다. 조회 실패 시 저장소 내 fallback 템플릿을 사용합니다.
- fallback evaluation prompt는 현재 v3 score-policy schema를 기준으로 유지해야 하며, LangSmith Prompt Hub의 `job-evaluation` lineage도 같은 JSON 계약과 점수 정책 문구로 동기화되어야 합니다. 로컬 fallback을 먼저 갱신한 뒤 Prompt Hub 최신 commit을 반영하고, 이후 `staging` 태그를 그 commit으로 이동해 offline experiment와 staged runtime이 같은 기준을 보도록 맞춥니다.
- curated fixture 기반 LangSmith dataset과 offline experiment 러너를 통해 프롬프트 버전, 모델, 점수 기준을 비교할 수 있습니다.
- 현재 골드 픽스처(gold fixture)는 단순 점수/통과 여부 외에 `expected_strength_keywords`, `expected_concern_keywords`, `expected_must_have_matches`, `expected_deal_breaker_flags`, `expected_confidence`까지 포함하며, fixture 로딩 시 계약 검증을 통과해야 합니다.
- production trace는 dataset 승격 후보로 추출할 수 있지만, v1에서는 수동 승인된 경우에만 dataset example로 추가합니다.

## 프롬프트 관리 가드레일 (Prompt Management Guardrails)

- 코드베이스 전반에 흩어놓지 말고 프롬프트를 모듈화하고 추적 가능하게 유지하세요.
- 구조화된 출력 스키마가 변경되면 프롬프트 지침, 파서 또는 검증기 로직, 그리고 테스트를 함께 업데이트하세요.

## 환경 전략 (Environment Strategy)

- 시작부터 dev와 prod 환경을 분리하세요.
- Dev는 전용 Supabase dev 프로젝트와 Slack 테스트 워크스페이스를 기본값으로 사용해야 합니다.
- Prod는 전용 Supabase 및 Slack 환경과 GitHub Actions CI/CD 및 스케줄링을 사용합니다.
- 데이터베이스, Slack 워크스페이스, OAuth 자격 증명 또는 API 키를 dev와 prod 간에 절대 공유하지 마세요.
- 로컬 개발 환경이 실수로 프로덕션 리소스를 가리키지 않도록 환경 변수를 명시적으로 분리 유지하세요.
- 스크래퍼는 `SCRAPER_HEADLESS`, `SCRAPER_TIMEOUT_MS`, `SCRAPER_MAX_PAGES`, `SCRAPER_INCRUIT_BASE_URL`로 제어하고, 로컬에서는 보수적인 페이지 제한을 유지하세요.
- 전용 dev 스케줄이 의도적으로 구성되지 않는 한 파이프라인 런타임 예약은 기본적으로 prod 전용으로 취급하세요.
- `APP_ENV`와 함께 별도의 `.env.development`, `.env.test`, `.env.production` 파일 사용을 표준화하세요.
- 로컬 SQLite는 격리된 테스트나 임시 부트스트래핑 용도로만 사용하고, 표준 모드 런타임 경로로 사용하지 마세요.

현재 스캐폴드 기본값:

- `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`는 PoC 런타임 경로에 필요한 백엔드 런타임 자격 증명입니다.
- 백엔드에서는 Next.js 웹 앱에서 인증된 브라우저 요청을 활성화하기 위해 `WEB_ORIGIN`도 읽습니다.
- `DATABASE_URL`은 필수 런타임 의존성이 아닌, 직접적인 Postgres 툴링 전용의 추가적인 도구용 레거시 설정입니다.
- `ALLOW_DEV_SCHEDULE=false`로 설정하여 명시적으로 활성화하지 않는 한 비프로덕션 스케줄링이 비활성화되도록 합니다.
- 웹 앱은 `NEXT_PUBLIC_API_BASE_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`를 읽습니다.

## 향후 작업을 위한 가드레일 (Guardrails For Future Work)

- 규칙 필터링이 제자리에 구현되기 전에 LLM 평가를 도입하지 마세요.
- 단일 사용자 PoC 루프가 작동하기 전에 멀티 테넌트 SaaS 복잡성을 최적화하지 마세요.
- 전체 파이프라인의 완료를 불안정한 스크래퍼의 성공에 의존하지 마세요.
- 피드백 기반 추천 루프에 맞게 스키마와 API를 정렬시키세요.
- 자유 형식 파싱보다 구조화된 출력체와 타입이 지정된 모델을 선호하세요.
- 테스트 커버리지를 후속 작업이 아닌 기능 전송의 일부로 취급하세요.
- 의미 있는 기능 구현이나 동작 변경에는 기대되는 동작을 포괄하는 자동화된 테스트가 포함되어야 합니다.
- 버그 수정은 가능한 한 회귀 테스트를 추가하거나 업데이트해야 합니다.

## 지연되거나 이후 단계를 위한 아이디어 (Deferred Or Later-Phase Ideas)

- 이력서 PDF 업로드 및 RAG 기반 온보딩 자동 완성
- 초기 PoC 사용자 외에 다수 기술 전문가들을 위한 보다 광범위한 SaaS 지원
- 핵심 추천 및 피드백 주기를 넘어선 보다 고급 대시보드 워크플로우

## 작업 시 가정 (Working Assumption)

구현 결정을 내릴 때 다음 사항들을 보존하는 가장 덜 복잡한 설계를 선호하세요:

- 엔드투엔드 PoC 운영 가능성
- 낮은 LLM 비용
- 피드백을 반영하는 추천 품질
- SaaS 아키텍처로의 미래 확장성
- 백엔드 `src/*`와 프론트엔드 `apps/web`의 현재 혼합 레이아웃
