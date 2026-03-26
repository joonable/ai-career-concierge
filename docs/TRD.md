# 🛠️ TRD: Scalable AI Job-Matching Agent System (Final)

## 1. System Architecture Overview

시스템은 크게 4개의 논리적 계층(Logical Layers)으로 구성되며, 각 계층은 API와 이벤트(Webhook)를 통해 느슨하게 결합(Loosely Coupled)됩니다.

- **Presentation Layer (Web UI & Chat Ops):** Next.js 기반의 사용자 대시보드 및 Slack 양방향 메시지(Block Kit).
- **Application Layer (API & Orchestration):** Python FastAPI 기반의 백엔드 서버. 에이전트 워크플로우(LangGraph)의 실행 컨텍스트를 제공하고 외부 요청을 라우팅.
- **Agentic Data Pipeline (Ingestion & Evaluation):** Playwright 기반의 데이터 수집 모듈과 Gemini 모델을 활용한 다단(Multi-stage) 평가 엔진.
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
    - `profile_data` (JSONB): 직무, 연차, 기술 스택 등 정형 데이터.
    - `guidelines` (JSONB): `must_haves`, `deal_breakers` 등 LLM 주입용 제약 조건.
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
4. **`DeliverNode`:** 기준 점수(예: 80점) 이상인 공고들을 포맷팅하여 Slack Interactive Webhook 발송.

## 6. Non-Functional Requirements (비기능 요구사항)

시스템의 안정성과 유지보수성을 보장하기 위한 핵심 정책입니다.

- **6.1 Observability & Tracing (관측성)**
    - **LLM Tracing:** `LangSmith` (Free Tier)를 연동하여 각 LangGraph 노드의 입력/출력, 소요 시간, 토큰 사용량, 그리고 환각(Hallucination) 여부를 시각적으로 모니터링합니다.
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