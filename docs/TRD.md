# 🛠️ TRD: Scalable AI Job-Matching Agent System (Final)

## 1. System Architecture Overview

시스템은 크게 4개의 논리적 계층(Logical Layers)으로 구성되며, 각 계층은 API와 이벤트(Webhook)를 통해 느슨하게 결합(Loosely Coupled)됩니다.

- **Presentation Layer (Web UI & Chat Ops):** Next.js 기반의 사용자 대시보드 및 Slack 양방향 메시지(Block Kit).
    - 내부 운영 가시성을 위해 `/internal` 운영 허브와 `/internal/prompts` 프롬프트 운영 패널을 둡니다.
    - `/internal` 운영 허브는 docs 기반 운영 문서 레지스트리, 최근 작업 보드, 다음 action/backlog, 검증 링크를 우선적으로 노출해야 합니다.
- **Application Layer (API & Orchestration):** Python FastAPI 기반의 백엔드 서버. 에이전트 워크플로우(LangGraph)의 실행 컨텍스트를 제공하고 외부 요청을 라우팅.
- **Agentic Data Pipeline (Ingestion & Evaluation):** Playwright 기반의 데이터 수집 모듈과 Gemini 모델을 활용한 다단(Multi-stage) 평가 엔진.
- **PromptOps Layer (Experimentation & Review):** Prompt family, experiment, evaluator, review workflow를 관리하는 내부 운영 계층. 현재는 저장소 내부 모듈로 시작하되 향후 분리 가능한 경계를 유지.
- **Storage Layer (Database & Auth):** Supabase (PostgreSQL) 기반의 영속성(Persistence) 데이터 및 사용자 인증 관리.

## 2. Infrastructure & Environment Isolation

SaaS 확장을 염두에 두고 처음부터 아키텍처를 이원화(Dev/Prod)하여 설계합니다.

- **Dev Environment (개발 환경):**
    - 로컬 DB 또는 Supabase Dev 프로젝트 사용.
    - Slack 테스트 워크스페이스 연동, 디버그 모드 활성화.
- **Prod Environment (운영 환경):**
    - Supabase Prod 프로젝트 사용.
    - 실제 운영용 Slack 워크스페이스 연동.
    - GitHub Actions를 통한 CI/CD 파이프라인 구축 및 스케줄링.

## 3. Component Specifications (핵심 기술 스택)

지엽적인 툴 종속성을 배제하고, 핵심 역할에 따른 스택을 정의합니다.

- **Frontend:** Next.js (React) - 서버 사이드 렌더링 및 정적 페이지 생성 활용.
- **Backend:** Python FastAPI (비동기 처리 최적화)
- **Agent Framework:** LangGraph (상태 기반 DAG 워크플로우)
- **LLM Provider:** Google Gemini Flash (JSON Structured Output 강제 적용)
- **Web Scraper:** Playwright (Python 비동기 환경)
- **Database & Auth:** Supabase (PostgreSQL, OAuth 2.0)
- **ORM:** SQLModel (Pydantic 기반, FastAPI 호환성 극대화)
- **Job Scheduler:** GitHub Actions (CRON 기반 외부 트리거 역할 수행)

## 4. Data Model (Core Schema)

상태 관리와 피드백 루프를 위한 4대 핵심 엔티티(Entity)입니다.

- **`User` (사용자)**
    - `id` (UUID, PK), `oauth_id`, `email`
    - `profile_data` (JSONB): 직무, 연차, 기술 스택 등 정형 데이터. 현재 PoC 온보딩 기준 필드는 `role`, `years_of_experience`, `title_keywords`.
    - `guidelines` (JSONB): `must_haves`, `deal_breakers` 등 LLM 주입용 제약 조건.
    - `notification_settings` (JSONB): `minimum_fit_score`, `delivery_channel` 등 추천 전달 기준. 현재 기본 채널은 `slack`.
- **`Job` (공고 원본 데이터)**
    - `id` (UUID, PK), `platform`, `external_job_id` (Unique - 중복 수집 방지)
    - `title`, `company`, `jd_raw_text` (공고 원문), `url`
- **`Evaluation` (평가 및 메모리 상태 - 핵심)**
    - `id` (UUID, PK)
    - `user_id` (FK), `job_id` (FK)
    - `status` (Enum): `PENDING` (평가 대기) → `RULE_REJECTED` (1차 탈락) → `LLM_EVALUATED` (2차 완료).
    - `fit_score` (Integer, Nullable), `reasoning` (Text)
    - `user_feedback` (Enum, Nullable): `LIKE`, `DISLIKE` (단기 기억 메모리로 활용)
- **`System_Log` (시스템 로그)**
    - 시스템 이벤트, 크롤링 실패 기록 등을 적재하여 대시보드 모니터링에 활용.

## 5. Agentic Workflow Design (LangGraph Architecture)

에이전트의 워크플로우는 LangGraph의 `StateGraph`로 정의되며, 철저히 모듈화되어 실행됩니다.

**[State Definition (`AgentState`)]** 파이프라인이 실행되는 동안 유지되는 전역 상태 객체입니다.

- `current_jobs`: List[Dict] (수집된 공고 큐)
- `user_context`: Dict (User DB에서 로드된 프로필 및 제약 조건)
- `recent_memory`: str (과거 `DISLIKE` 피드백 요약본)
- `evaluation_results`: List[Dict] (최종 평가가 완료된 결과 배열)

**[Node Flow]**

1. **`IngestNode`:** 타겟 채널(예: 인크루트) 비동기 스크래핑 → `Job` DB 적재 및 중복 필터링.
2. **`RuleFilterNode`:** DB 쿼리(연차, 직무 키워드 등)를 통한 1차 Hard Filtering → `Evaluation` 상태 업데이트.
3. **`LLMEvalNode`:** (비용 발생 구간) Rule 노드를 통과한 공고들을 Batch로 묶어 Gemini API 호출 → Deal-breaker 분석 및 점수화.
    - Structured output 기본 계약은 `fit_score`, `summary`, `strengths`, `concerns`, `must_have_matches`, `deal_breaker_flags`, `confidence`, `role_alignment`, `must_have_coverage`, `deal_breaker_severity`, `transferable_skills`를 포함합니다.
4. **`DeliverNode`:** 기준 점수(예: 80점) 이상인 공고들을 포맷팅하여 Slack Interactive Webhook 발송.

## 6. Non-Functional Requirements (비기능 요구사항)

시스템의 안정성과 유지보수성을 보장하기 위한 핵심 정책입니다.

- **6.1 Observability & Tracing (관측성)**
    - **LLM Tracing:** `LangSmith` (Free Tier)를 연동하여 사용자별 파이프라인 실행을 root trace로, Gemini 평가 호출을 child trace로 기록합니다.
    - 파이프라인 trace에는 `run_id`, `user_id`, `dry_run`, `app_env`, `pipeline_version`, `user_profile_role`, `minimum_fit_score`, `delivery_channel`과 memory-summary prompt의 `prompt_tag`, `prompt_commit_hash`를 metadata로 남기고, Gemini trace에는 `evaluation_id`, `job_id`, `external_job_id`, `platform`, `title`, `job_company`, `prompt_name`, `prompt_version`, `prompt_variant`, `schema_version`, `prompt_identifier`, `prompt_reference`, `prompt_tag`, `prompt_commit_hash`, `model`, `latency_ms`를 남깁니다.
    - `LANGSMITH_API_KEY`가 없으면 tracing은 비활성화되고 기존 애플리케이션 로그와 `System_Log` 기반 관측만 유지됩니다.
    - Prompt Hub 자산은 `LANGSMITH_EVAL_PROMPT_IDENTIFIER`, `LANGSMITH_MEMORY_PROMPT_IDENTIFIER`를 통해 태그 기준(`:staging`, 필요 시 `:production`)으로 선택하고, 조회 실패 시 로컬 fallback prompt를 사용합니다.
    - 실험 비교는 선별된 골드 데이터셋(curated gold dataset)과 LangSmith experiment workflow를 통해 수행하고, production trace는 수동 승인 흐름으로 dataset candidate에 승격합니다.
    - 선별된 골드 데이터셋은 pass/fail과 점수대만 아니라 구조화 설명 품질까지 평가할 수 있도록 strength/concern keyword, must-have/deal-breaker expectation, confidence expectation을 포함해야 합니다.
    - **Application Logging:** FastAPI의 내장 Structured Logging을 사용하여 API 호출 및 일반 시스템 에러를 기록합니다.
- **6.2 Resilience & Fallback Policy (복원력 및 장애 대응)**
    - **Graceful Degradation (우아한 기능 저하):** 채용 사이트(예: 인크루트)의 DOM 구조 변경 등으로 Playwright 스크래핑이 실패하더라도 전체 파이프라인은 중단되지 않습니다.
    - **Error Handling:** 에러가 발생한 플랫폼은 건너뛰고(Skip) 나머지 플랫폼의 수집 및 평가를 계속 진행합니다.
    - **Failure Logging:** 스크래핑 실패 내역은 `System_Log` DB에 기록하고, 지정된 Slack 알림 채널(예: `#system-alerts`)로 관리자에게 즉시 리포트하여 빠른 유지보수를 돕습니다.

## 7. Interface & Integration (API & Webhook 규약)

시스템 외부(Slack, Frontend, 스케줄러)와의 통신 규약입니다.

- **`POST /api/v1/pipeline/trigger`**
    - GitHub Actions가 스케줄에 맞춰 호출하는 트리거 엔드포인트. 보안을 위해 내부 API Key(`X-API-Key`) 헤더를 검증합니다.
- **`POST /api/v1/slack/interactive-webhook`**
    - Slack에서 사용자가 👍/👎 버튼 클릭 시 Action payload를 수신합니다. DB의 `Evaluation` 테이블 업데이트 로직을 수행하고 성공 시 HTTP 200을 반환합니다.
- **`GET /api/v1/users/me/dashboard`**
    - Next.js 프론트엔드에서 칸반 보드를 렌더링하기 위한 개인화된 추천 공고 목록을 반환합니다.
    - 각 추천 항목은 기본 평가 필드 외에도 상세 패널용 구조화 필드(`decision_summary`, `match_highlights`, `risk_highlights`, `confidence_level`, `rule_match_reasons`, `rule_rejection_details`, `responsibilities`, `requirements`, `preferred_requirements`, `location`, `employment_type`)를 포함합니다.
    - 위 구조화 필드는 현재 PoC 단계에서 DB에 별도 컬럼으로 저장하지 않고, 공고 원문/메타데이터와 사용자 프로필, 평가 결과를 바탕으로 백엔드에서 파생하여 응답합니다.
- **`GET /api/v1/users/me/promptops-status`**
    - 내부 PromptOps 운영 패널용 read-only 스냅샷 응답을 반환합니다.
    - 응답은 production/staging/candidate prompt 식별자, latest decision, LangSmith compare / annotation queue 링크, Notion backlog 링크, 최신 iteration 링크, 최신 요약과 backlog top 3를 포함합니다.
    - 접근 제어는 Supabase 세션 기반 bearer 인증 위에 `PROMPTOPS_ADMIN_EMAILS` allowlist를 추가로 적용합니다.

## 8. Internal Operations Panel Contract

- `/internal` 운영 허브는 문서 기반 운영 패널로 정의합니다.
- 운영 패널은 최소한 다음 기능을 지원하는 방향으로 설계합니다:
    - 핵심 문서 레지스트리 노출: `AGENTS.md`, `docs/CONTEXT.md`, `docs/TRD.md`, `docs/PRD.md`, 운영 패널 관련 `.md`
    - 문서 편집 진입점 또는 수정 동선 제공
    - 최근 완료 작업, 현재 작업 상태, 다음 action, backlog 노출
    - 각 작업에 대한 UI 확인 경로 또는 검증 링크 노출
    - PromptOps, scraper, pipeline, delivery 같은 운영 모듈 상태를 additive하게 합류시킬 수 있는 카드형 구조
- 운영 패널의 docs canonical source는 우선 다음 문서 집합입니다:
    - `docs/internal/status.md`
    - `docs/internal/operations_panel.md`
    - `docs/internal/agent_workboard.md`
- `docs/internal/agent_workboard.md`는 에이전트가 작업 완료 시 갱신하는 운영용 현재 상태 문서이며, 운영 패널은 이를 1차 요약 source로 사용할 수 있어야 합니다.
- 문서 편집 기능이 아직 구현되지 않았더라도, TRD 기준으로 운영 패널은 적어도 문서 보기/링크/업데이트 책임을 구조적으로 수용해야 합니다.

## 9. PromptOps Architecture Boundary

- PromptOps는 이 저장소 안에서 시작하는 내부 운영 모듈이며 경로는 `src/promptops`입니다.
- 공통 운영 개념(prompt family metadata, experiment spec, review item, failure taxonomy, iteration record)은 `src/promptops/core`에 둡니다.
- 외부 backend 연동은 `src/promptops/adapters` 아래에 두고, LangSmith는 첫 번째 adapter로 사용합니다.
- AI Career Concierge 특화 로직(평가 policy 의미, dataset bindings, review rubric, normalized context)은 `src/promptops/projects/ai_career_concierge`에 둡니다.
- 이 경계는 향후 PromptOps core를 별도 패키지나 프로젝트로 분리할 수 있게 하기 위한 설계 규칙입니다.
- 내부 운영 허브는 docs 기반 운영 요약, 작업 보드, 핵심 문서 레지스트리와 PromptOps 상태 스냅샷을 함께 보여주고, `/internal/prompts`는 LangSmith/Notion의 live backend를 직접 호출하지 않고 백엔드가 제공하는 수동 PromptOps 상태 스냅샷을 렌더링합니다.
