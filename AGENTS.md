# AGENTS.md

## 목적 (Purpose)

이 저장소는 노이즈가 많은 채용 공고를 필터링하고 적합도가 높은 기회만 추천하는 AI 기반 채용 매칭 시스템인 **AI Career Concierge**를 구축합니다.

현재 단계는 **단일 사용자 PoC(개념 증명)**입니다. 모든 구현 결정은 범위를 확장하기 전에 한 명의 주요 사용자를 위해 엔드투엔드 루프가 안정적으로 작동하도록 하는 것을 최우선으로 해야 합니다.

## 단일 진실 공급원 (Source Of Truth)

이 저장소에서 작업할 때는 다음 순서로 문서를 참조하세요:

1. [`docs/CONTEXT.md`](docs/CONTEXT.md)
2. [`docs/TRD.md`](docs/TRD.md)
3. [`docs/PRD.md`](docs/PRD.md)
4. [`docs/internal/operations_panel.md`](docs/internal/operations_panel.md)
5. [`docs/internal/agent_workboard.md`](docs/internal/agent_workboard.md)

충돌이 발생하는 경우:

- `CONTEXT.md`는 일상적인 구현을 위한 작업 요약입니다.
- `TRD.md`는 아키텍처 및 기술 계약을 정의합니다.
- `PRD.md`는 제품 의도와 비즈니스 목표를 정의합니다.
- `docs/internal/operations_panel.md`는 `/internal` 운영 패널이 어떤 문서와 상태를 노출/편집해야 하는지 정의합니다.
- `docs/internal/agent_workboard.md`는 최근 작업, 현재 상태, 다음 action, backlog의 운영용 현재 상태를 기록합니다.

중요한 충돌인 경우, 추측하지 말고 작업을 멈추고 명시적으로 해결하세요.

## 현재 제품 범위 (Current Product Scope)

PoC는 다음 루프를 지원해야 합니다:

1. 사용자가 Google로 로그인하여 프로필을 구성합니다.
2. 시스템이 대상 플랫폼에서 채용 공고를 수집(ingest)합니다.
3. 공고는 2단계 평가 파이프라인을 거칩니다:
   - 규칙 기반 필터링 (rule-based filtering)
   - LLM 기반 심층 평가 (LLM-based deep evaluation)
4. 높은 점수를 받은 공고는 Slack을 통해 전달됩니다.
5. 사용자는 좋아요/싫어요(like/dislike) 피드백을 제공합니다.
6. 최근의 싫어요 피드백은 단기 기억(short-term memory)으로 저장되어 이후 평가에 재사용됩니다.

## 제품 우선순위 (Product Priorities)

- 재현율(recall)보다 정밀도(precision) 최적화.
- 모델 호출 전 공격적인 필터링으로 LLM 비용 절감.
- 향후 추천을 개선하는 깔끔한 피드백 루프 유지.
- 섣부른 SaaS 일반화보다 엔드투엔드 서비스 작동 우선.

## 확정된 기술 스택 (Confirmed Technical Stack)

- 프론트엔드: Next.js
- 백엔드: FastAPI
- 워크플로우 오케스트레이션: LangGraph
- LLM: 구조화된 JSON 출력이 가능한 Google Gemini Flash
- 스크래핑: Python async 런타임의 Playwright
- 데이터베이스 및 인증: Supabase PostgreSQL + Google OAuth
- 런타임 영속성(persistence): 서비스 역할 액세스(service role access)가 있는 Supabase Data API
- 레거시 스키마 참조: SQLModel
- 스케줄링: GitHub Actions cron 트리거
- 추적(Tracing): LangSmith

명확한 이유와 사용자의 명시적 승인 없이 이를 교체하지 마세요.

## 환경 분리 (Environment Separation)

이 프로젝트는 개발(development)과 프로덕션(production) 간의 명시적인 분리를 가정합니다.

- dev와 prod에 대해 별도의 Supabase 프로젝트를 사용하세요.
- dev와 prod에 대해 별도의 Slack 워크스페이스나 앱 자격 증명을 사용하세요.
- 제공자(provider) 설정에서 요구하는 경우 별도의 OAuth 자격 증명을 사용하세요.
- 모든 외부 연동에 대해 별도의 API 키와 시크릿을 사용하세요.
- 기본적으로 로컬 개발 환경이 프로덕션 리소스를 가리키도록 하지 마세요.

운영 규칙:

- 개발 환경은 테스트, 디버깅 및 스크래퍼 반복 작업에 안전해야 합니다.
- 사용자가 명시적으로 dev 스케줄을 활성화하지 않는 한, 프로덕션 환경만 실제 예약된 전송(scheduled delivery)을 실행해야 합니다.

## 폴더 구조 원칙 (Folder Structure Principles)

TRD의 시스템 계층과 일치하고 경계를 명확하게 유지하는 저장소 구조를 선호합니다.

현재 저장소의 구현 구조:

- `apps/web`
  - 로그인, 인증 콜백, 온보딩 및 대시보드 흐름을 위한 Next.js App Router 프론트엔드
  - 페이지 라우트는 `src/app`에, 재사용 가능한 UI는 `src/components`에, 런타임 연동 코드는 `src/lib`에 유지

- `src/api`
  - FastAPI 라우트, 오케스트레이션 진입점, 인증 및 연동 핸들러
- `src/agent`
  - LangGraph 워크플로우, 프롬프트 빌더, 평가 스키마 및 노드 구현
- `src/scraper`
  - Playwright 기반의 수집 로직 및 소스별 스크래퍼
- `src/db`
  - PoC 전환 기간 동안 유지되는 레거시 SQLModel 모델, 마이그레이션 기록 및 스키마 참조
- `src/common`
  - 공유 설정, 로깅, 상수 및 타입이 지정된 유틸리티 모듈
- `tests`
  - 단위, 통합, 계약 및 엔드투엔드 테스트
- `docs`
  - 제품 및 기술 관련 문서
  - `/internal` 운영 패널에서 노출할 운영 문서와 작업 보드 포함

나중에 프로젝트가 현재의 PoC 이상으로 성장하면 다음과 같은 구조로 발전할 수 있습니다:

- `apps/api`
- `packages/agent`
- `packages/scraper`
- `packages/db`
- `packages/common`

폴더 규칙:

- 모호한 헬퍼(helper) 대신 도메인 및 책임별로 그룹화하세요.
- 프레임워크 진입점은 가볍게 유지하고 비즈니스 로직은 재사용 가능한 모듈로 밀어 넣으세요.
- 일반적인 평가 모듈에 Slack 연동 로직을 두지 마세요.
- 한 소스의 오류가 다른 소스를 오염시키지 않도록 스크래퍼 구현은 소스별로 격리하세요.
- 공유 스키마 및 설정을 여러 계층에 복제하지 말고 예측 가능한 단일 위치에 두세요.

## 모듈 설계 규칙 (Module Design Rules)

- `evaluation_service.py`, `slack_notifier.py`, `pipeline_state.py`와 같은 명시적인 이름을 선호하세요.
- 도메인 특화된 이름이 가능한 경우 `utils.py` 같은 포괄적인 파일 이름은 피하세요.
- 프롬프트 빌드 로직은 전송(transport) 또는 제공자 클라이언트(provider client)와 분리하세요.
- 책임이 나뉘는 경우 API 요청 모델, 도메인 모델 및 영속성 모델을 별개로 유지하세요.
- 필터링, 점수 정규화 및 프롬프트 조립의 경우 가능한 한 순수 함수(pure functions)를 선호하세요.

## 아키텍처 규칙 (Architecture Rules)

- 프레젠테이션, API/오케스트레이션, 에이전트 파이프라인, 스토리지 계층 간에 시스템을 느슨하게 결합(loosely coupled)하도록 유지하세요.
- 평가 파이프라인을 LangGraph `StateGraph`로 모델링하세요.
- 스크래핑, 규칙 필터링, LLM 평가 및 전달(delivery)은 별도의 관심사로 유지하세요.
- 임의의 dict 파싱보다 타입이 지정된 모델과 구조화된 출력을 선호하세요.
- 피드백 기반 추천 워크플로우에 맞게 스키마와 API를 일치시키세요.

## 현재 인증 경계 (Current Auth Boundary)

- 웹 앱은 Next.js App Router SSR 세션 패턴을 통해 Supabase Google OAuth를 사용해야 합니다.
- 보호된 프론트엔드 라우트는 커스텀 로컬 인증 상태가 아닌 Supabase 세션 쿠키에 의존해야 합니다.
- FastAPI는 `Authorization: Bearer <Supabase access token>`을 백엔드 인증 계약으로 취급해야 합니다.
- 백엔드 토큰 검증은 구성된 프로젝트 JWKS에 대해 Supabase JWT를 확인하고 토큰 클레임에서 안정적인 사용자 ID를 추출해야 합니다.
- 백엔드 프로필, 대시보드, 피드백 및 파이프라인 영속성은 현재 PoC 런타임을 위해 `SUPABASE_SERVICE_ROLE_KEY`와 함께 Supabase Data API를 사용해야 합니다.

## 핵심 워크플로우 계약 (Core Workflow Contract)

예상되는 LangGraph 노드 흐름은 다음과 같습니다:

1. `IngestNode`
2. `RuleFilterNode`
3. `LLMEvalNode`
4. `DeliverNode`

공유 파이프라인 상태는 다음을 포함해야 합니다:

- `current_jobs`
- `user_context`
- `recent_memory`
- `evaluation_results`

규칙 필터링을 우회하고 스크래핑된 원시 공고를 LLM 평가로 직접 보내지 마세요.

## 데이터 모델 예상 사항 (Data Model Expectations)

핵심 엔티티:

- `User`
- `Job`
- `Evaluation`
- `System_Log`

최소 평가 수명 주기:

- `PENDING`
- `RULE_REJECTED`
- `LLM_EVALUATED`

최소 피드백 상태:

- `LIKE`
- `DISLIKE`

중요 불변성(Invariants):

- 중복 수집을 방지하기 위해 `Job.external_job_id`는 소스별로 고유해야 합니다.
- 규칙 기반 거부(rejection)도 평가 상태로 유지(persist)되어야 합니다.
- 싫어요 피드백은 사용 가능한 경우 이유와 함께 저장할 수 있어야 합니다.

## 마이그레이션 규칙 (Migration Rules)

- 데이터베이스 스키마 변경을 로컬 리팩터링이 아닌 계약 변경으로 취급하세요.
- 모든 스키마 변경에는 순방향 마이그레이션(forward migration) 경로와 문서화된 롤백(rollback) 또는 호환성(compatibility) 계획이 포함되어야 합니다.
- 현재 PoC 런타임의 경우 스키마 변경 워크플로우로 Supabase SQL/MCP를 선호하세요.
- 저장소 내 전환 기간 동안 레거시 SQLModel 참조, 데이터베이스 스키마, 상태 enum 및 API 측 가정을 동기화하여 유지하세요.
- 스키마 변경이 API 응답, 평가 수명 주기 또는 피드백 동작에 영향을 미치는 경우 같은 변경 내에서 테스트와 문서를 업데이트하세요.
- 정리(cleanup) 속도보다 호환성이 중요할 때는 추가적(additive) 또는 단계적(staged) 마이그레이션을 선호하세요.

## 필수 외부 인터페이스 (Required External Interfaces)

다음 엔드포인트와의 호환성을 유지하세요:

- `POST /api/v1/pipeline/trigger`
- `POST /api/v1/slack/interactive-webhook`
- `GET /api/v1/users/me/dashboard`

`POST /api/v1/pipeline/trigger`는 내부 `X-API-Key`를 검증해야 합니다.

## API 변경 규칙 (API Change Rules)

- 요청 및 응답 스키마, 인증 동작, 웹훅 페이로드, 공개 상태 enum을 퍼블릭 계약으로 취급하세요.
- 모든 API 계약 변경 시 타입 지정 스키마, 핸들러, 문서 및 자동화된 테스트를 같은 변경 내에서 업데이트해야 합니다.
- 브레이킹 체인지(Breaking changes)는 최종 요약 또는 변경 노트에서 명시적으로 언급되어야 합니다.
- 계약 변경을 확정하기 전에 대시보드, Slack 연동, 스케줄러 트리거, 저장된 평가 데이터에 미치는 하위 영향을 확인하세요.

## 구성 및 환경 변수 규칙 (Configuration And Environment Variable Rules)

- 구성 로딩을 런타임당 하나의 모듈로 중앙집중화하세요.
- 환경 변수를 한 번만 읽고, 조기에 검증하며, 타입이 지정된 설정(settings) 객체를 노출하세요.
- 프로덕션 직면 코드 경로에서 필수 시크릿이 누락된 경우 즉시 실패(fail fast)하도록 하세요.
- 로컬 기본값은 최소한으로 안전하게 유지하세요.

명명 규칙:

- 모든 환경 변수에 대문자 스네이크 케이스(uppercase snake case)를 사용하세요.
- 유용한 경우 하위 시스템별로 변수에 접두사를 붙이세요:
  - `SUPABASE_*`
  - `GOOGLE_*`
  - `SLACK_*`
  - `LANGSMITH_*`
  - `GEMINI_*`
- 현재 환경에서 선택한 활성 런타임 구성에는 다음과 같은 일반적인 이름을 사용하세요:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SLACK_BOT_TOKEN`
- 활성 런타임 환경을 나타내기 위해 `APP_ENV`를 사용하세요 (값 예시: `development`, `test`, `production`).
- 애플리케이션 코드 내에서 모든 변수에 환경 이름을 접미사로 붙이는 대신 `.env.development`, `.env.test`, `.env.production`과 같이 분리된 env 파일을 사용하는 것을 선호하세요.
- 격리된 테스트 구성이 필요한 경우에만 `_TEST`와 같은 명시적인 접미사를 사용하세요.

시크릿 처리 규칙:

- 절대 시크릿을 하드코딩하지 마세요.
- 실제 `.env` 파일을 절대 git에 커밋하지 마세요.
- 프로덕션 시크릿을 개발이나 테스트에서 재사용하지 마세요.
- 서비스 역할 키와 웹훅 서명 시크릿은 높은 민감도로 취급하세요.
- `DATABASE_URL`을 레거시 선택적 툴링 값으로 취급하고 PoC 경로에 필요한 기본 런타임 시크릿으로 취급하지 마세요.

## 프롬프트 관리 규칙 (Prompt Management Rules)

- 라우트, 서비스 또는 테스트 전반에 인라인으로 흩어놓지 말고 전용 모듈이나 템플릿에 프롬프트를 보관하세요.
- 동작이 진화하더라도 프롬프트 사용을 추적할 수 있도록 목적에 따라 프롬프트 이름을 지정하세요.
- 프롬프트 지침, 구조화된 출력 스키마, 파싱 로직, 검증 테스트를 같은 변경 내에서 정렬하세요.
- 구조화된 출력 스키마 변경 시 프롬프트 텍스트, 파서/검증기 로직, 그리고 자동화된 테스트를 함께 업데이트해야 합니다.

## 옵저버빌리티(관측성) 규칙 (Observability Rules)

- 파이프라인 실행마다 추적 가능한 `run_id` 또는 `trace_id`를 방출(emit)하고 가능한 경우 하위 작업 전반에 재사용하세요.
- 파이프라인 작업을 위한 구조화된 로그에는 `run_id`, `user_id`, `job_id`, `platform`, `status`, `error_type`의 관련된 하위 집합이 포함되어야 합니다.
- 스크래퍼 실패, 평가 상태 전환, LLM 호출, Slack 전송 시도, 웹훅 동작을 구조화된 형식으로 기록하세요.
- 시크릿, 액세스 토큰, 원시 웹훅 서명 또는 불필요한 개인 식별 정보(PII)를 기록하지 마세요.

## 안정성 요구 사항 (Reliability Requirements)

- 한 플랫폼에서의 스크래핑 실패가 전체 파이프라인을 중단시켜서는 안 됩니다.
- 실패한 소스는 건너뛰고 기록되며 운영상 보고되어야 합니다.
- 중요한 실패는 `System_Log`에 기록할 수 있어야 합니다.
- 시스템은 스크래퍼가 손상되었을 때 정상적으로 저하(degrade gracefully)되어야 합니다.

## 범위 가드레일 (Scope Guardrails)

PoC 루프가 작동하기 전에 다음 작업에 시간을 낭비하지 마세요:

- 다중 테넌트(multi-tenant) SaaS 복잡성
- 이력서 업로드 및 RAG 온보딩
- 추천 검토 및 피드백을 넘어선 고급 대시보드 기능
- 핵심 루프에 필요하지 않는 한, 많은 채용 플랫폼에 대한 광범위한 최적화

## 구현 지침 (Implementation Guidance)

- 나중에 확장될 수 있는 단순한 설계를 선호하세요.
- 작동하는 수직 슬라이스(vertical slice)가 존재하기 전에는 불필요한 추상화(over-engineering)를 피하세요.
- 아키텍처 계약을 유지하면서 각 계층의 가장 작고 유용한 버전을 구축하세요.
- LLM 사용을 좁고 타입에 맞으며 관찰하기 쉽게 유지하세요.
- 특히 스크래핑 및 외부 연동과 관련된 실패 경로를 명시적으로 만드세요.
- 환경별 분기 처리가 명시적이고 테스트 가능하도록 환경 로딩을 중앙집중화하세요.
- 값이 공유되는지, dev 전용인지, 또는 prod 전용인지 명확하도록 구성 필드 이름을 지정하세요.
- 스크래퍼, LLM, Slack 연동을 테스트에서 모킹(mock)할 수 있도록 이음새(seams)를 추가하세요.
- 직접적인 Postgres 접근을 도입할 명확한 이유가 없다면 새로운 영속성 작업에는 Supabase Data API 경로를 선호하세요.
- 작업 결과를 사용자가 직접 확인할 수 있다면, 가능할 때마다 UI에서 검증 가능한 형태로 수직 슬라이스를 마무리하세요.
- 내부 운영 가시성이 중요해지는 변경은 `/internal` 운영 패널에서 문서 또는 상태판 형태로 바로 확인할 수 있게 만드는 것을 선호하세요.

## 테스트 우선순위 (Testing Priorities)

테스트는 단순한 코드 커버리지가 아닌 제품 리스크를 따라야 합니다.

가장 높은 우선순위:

- 규칙 기반 필터링 동작
- 평가 상태 전환
- 피드백 저장 및 메모리 요약 동작
- 구성 로딩 및 환경 분리 안전장치
- `X-API-Key`를 사용한 파이프라인 트리거 인증

두 번째 우선순위:

- LLM 구조화된 출력의 파싱 및 검증
- Slack 페이로드 포맷팅 및 웹훅 처리
- 스크래퍼 정규화 및 중복 제거 동작
- 대시보드 응답 형태 만들기

초기 PoC에서 낮은 우선순위:

- 광범위한 UI 스냅샷 커버리지
- 채용 플랫폼 스크래퍼에 대한, 존재하지도 않는 철저한 테스트
- 단순한 프레임워크 연결을 위한 가치 없는 단위 테스트

테스트 형태 지침:

- 빠른 단위 테스트 하에 순수한 로직을 먼저 배치하세요.
- DB 기반 평가 흐름 및 API 핸들러에 대한 통합 테스트를 추가하세요.
- 구조화된 LLM 출력 및 Slack 요청 페이로드에 대한 계약 테스트를 추가하세요.
- 스크래퍼의 경우 고정 데이터(fixture) 기반 파싱 테스트를 선호하고, 필요한 경우 소수의 안전장치가 마련된 실시간 검사(live checks)를 추가하세요.
- 필터링, 점수 매기기, 피드백 또는 중복 제거의 모든 버그에 대해 회귀 테스트(regression tests)를 추가하세요.

새 기능 작업에 대한 최소 요구 사항:

- 의미 있는 모든 기능 개발에는 제공된 동작을 커버하는 자동화된 테스트가 포함되어야 합니다.
- 새로운 비즈니스 로직은 코드가 일시적인 스캐폴딩이 아닌 이상 최소한 하나의 자동화된 테스트와 함께 제공되어야 합니다.
- 버그 수정에는 가능한 한 회귀 테스트가 포함되어야 합니다.
- 의도적으로 테스트를 건너뛰는 경우 최종 업데이트에서 그 이유를 문서화하세요.

## 완료 조건 (Definition Of Done)

관련된 변경 사항에 다음이 포함될 때까지 기능이나 버그 수정은 완료된 것이 아닙니다:

- 구현 코드
- 제공된 동작에 대한 자동화된 테스트
- 동작이나 인터페이스가 변경될 때의 문서 또는 계약 업데이트
- 운영자가 `/internal`에서 확인해야 하는 상태가 바뀌는 경우 관련 운영 문서 업데이트
- 설정이 변경될 때의 환경 변수 또는 구성 템플릿 업데이트
- 새롭거나 변경된 실행 경로에 대한 로깅 및 오류 처리 검토

구현만 된 변경 사항은 완료된 제공으로 간주되지 않습니다.

## 에이전트 작업 규범 (Working Norms For Agents)

- 상당한 수정을 하기 전에 `docs/CONTEXT.md`를 읽으세요.
- 사용자가 변경을 요청하지 않는 한 현재 스택과 아키텍처를 유지하세요.
- 새 모듈을 추가할 때 이름을 명시적이고 제품 개념과 일치하도록 유지하세요.
- 작업을 마친 뒤 가능하다면 사용자가 UI에서 직접 결과를 확인할 수 있도록 구현, 연결, 또는 검증 경로까지 함께 정리하세요.
- 의미 있는 작업을 마치면 `docs/internal/agent_workboard.md`와 필요 시 `docs/internal/status.md`를 업데이트해 `/internal` 운영 패널에서 최신 작업 맥락이 보이게 유지하세요.
- 불확실할 때에는 다음을 가장 잘 지원하는 경로를 선택하세요:
  - 엔드투엔드 PoC 운영 가능성
  - 낮은 LLM 비용
  - 피드백을 반영하는 추천 품질
  - 현재의 복잡성 없이 달성가능한 미래 SaaS 확장성

## 문서화 규칙 (Documentation Rule)

구현으로 인해 아키텍처, API 계약, 핵심 데이터 모델 또는 워크플로우 가정이 변경되는 경우 다음 위치의 관련 문서를 업데이트하세요:

- `docs/CONTEXT.md`
- `docs/TRD.md`
- `docs/PRD.md`
- `docs/internal/operations_panel.md`
- `docs/internal/agent_workboard.md`
- `docs/internal/status.md` (운영 패널에 보여줄 현재 상태가 바뀌는 경우)

`docs/CONTEXT.md`는 간결하고 구현 중심으로 유지하세요.

참조 문서와 운영 문서는 기본적으로 한국어를 우선 사용하세요. 영어 표현이 꼭 필요할 때만 괄호로 병기하고, 특별한 이유가 없다면 영어 문장만 단독으로 남기지 마세요.

## 저장소 규칙 (Repository Conventions)

- 시크릿은 git에 포함하지 마세요.
- 실제 `.env` 파일은 절대 커밋하지 말고 `.env.example`과 같은 템플릿만 커밋하세요.
- 구성을 추가할 때 `.env.development`와 `.env.production` 모두 깔끔하게 지원할 수 있는 구조를 선호하세요.
- 생성된 결과물과 로컬 캐시를 버전 제어에서 제외하세요.
- 문서는 계약을 정의할 때의 구현에 가깝게 유지하되, 높은 수준의 제품 및 아키텍처 문서는 `docs/` 아래에 보관하세요.
