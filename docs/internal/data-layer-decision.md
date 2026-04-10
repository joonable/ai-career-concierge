# 데이터 계층 이중 구조 정리 방향 결정

**작성일**: 2026-04-10
**상태**: 결정 완료 (Phase 5-2)
**대상 독자**: 개발팀, 에이전트

---

## 1. 배경

현재 PoC 코드베이스에는 두 가지 데이터 접근 경로가 공존한다.

- **경로 A**: Supabase Data API (`SupabaseRestClient` + `httpx`) — 운영 런타임
- **경로 B**: SQLModel + Alembic + `Session` — 레거시 참조 및 테스트 인프라

이 문서는 각 경로의 실제 사용 현황을 분석하고 PoC 단계 기준의 정리 방향을 결정한다.

---

## 2. 현재 이중 구조 사용 현황

### 2-1. 경로 A — Supabase Data API (운영 런타임)

**핵심 구현**: `src/api/services/supabase_storage.py`

운영 런타임의 모든 CRUD 작업은 `SupabaseRestClient`(httpx 기반 REST 클라이언트)를 통해 수행된다.

| 스토어 클래스 | 역할 | 사용처 |
|---|---|---|
| `SupabaseRestClient` | HTTP REST 기반 Supabase Data API 클라이언트 | 하위 스토어 전체가 공유 |
| `SupabaseUserStore` | 사용자 upsert, 프로필 조회/수정 | `/api/v1/users/*` 라우트 |
| `SupabaseEvaluationStore` | 평가 생성/상태 전환/피드백 저장/대시보드 조회 | `/api/v1/pipeline/trigger`, `/api/v1/evaluations/*`, `/api/v1/users/me/dashboard` |
| `SupabaseJobStore` | 채용 공고 upsert (중복 제거 포함) | `/api/v1/pipeline/trigger` |
| `SupabaseSystemLogStore` | 파이프라인 이벤트 로그 기록 | `/api/v1/pipeline/trigger`, Slack 라우트 |

**의존성 주입 경로**: `src/api/dependencies/supabase_store.py` → 각 라우트 `Depends(get_*_store)`

`db.enums` 모듈(`EvaluationStatus`, `FeedbackState`, `LogLevel`)은 경로 A에서도 공유하여 사용한다.

### 2-2. 경로 B — SQLModel + Alembic (레거시/테스트용)

**핵심 구현**: `src/db/`

| 구성 요소 | 파일 위치 | 역할 |
|---|---|---|
| SQLModel 모델 | `src/db/models/{user,job,evaluation,system_log}.py` | 테이블 스키마 정의 (Python ORM 클래스) |
| Alembic 마이그레이션 | `src/db/migrations/versions/` | 스키마 이력 관리 (2개 버전) |
| Repository 클래스 | `src/db/repositories/{user,job,evaluation,system_log}_repository.py` | SQLModel Session 기반 CRUD 래퍼 |
| `session.py` | `src/db/session.py` | SQLAlchemy 엔진 및 세션 팩토리 |
| `database.py` dependency | `src/api/dependencies/database.py` | `get_session` 노출 (FastAPI Depends용) |

**운영 런타임에서 실제 호출되는가?**

- `get_session` / Repository 클래스는 **운영 라우트에서 직접 주입되지 않는다**.
- `src/api/dependencies/database.py`는 `get_session`을 재노출하지만, 실제 라우트(`users.py`, `evaluations.py`, `pipeline.py`, `slack.py`)에서 `Depends(get_session)`을 사용하는 코드는 없다.
- `src/agent/schemas/pipeline_job.py`의 `PipelineJob.from_job_model(job: Job)` 메서드는 SQLModel `Job` 모델을 인자로 받는 클래스 메서드를 정의하지만, 운영 파이프라인에서는 호출되지 않는다. (`SupabaseJobStore.upsert_job()`이 직접 `PipelineJob`을 반환한다.)
- `src/agent/nodes/`와 `src/api/services/`에서 `db.enums`만 공유 임포트하며, 모델과 세션은 임포트하지 않는다.

**테스트에서의 사용**

테스트 인프라(`tests/conftest.py`)는 전적으로 SQLModel + SQLite 기반으로 구성된다.

- `FakeUserStore`, `FakeEvaluationStore`, `FakeJobStore`, `FakeSystemLogStore`: 각 Repository를 내부에서 사용하며 운영 Store의 인터페이스를 흉내 낸다.
- `app` 픽스처에서 `application.dependency_overrides`를 통해 운영 Supabase Store를 SQLite 기반 Fake Store로 교체한다.
- `test_env` 픽스처에서 `DATABASE_URL=sqlite:///...`를 설정하고 `SQLModel.metadata.create_all(engine)`로 스키마를 초기화한다.

---

## 3. 각 경로의 장단점

### 경로 A — Supabase Data API

**장점**
- 운영 환경(Supabase PostgreSQL)과 동일한 경로를 사용하므로 환경 불일치(dev/prod gap)가 적다.
- Supabase의 Row Level Security(RLS), Realtime, Storage 등 플랫폼 기능과 자연스럽게 연동 가능하다.
- `SUPABASE_SERVICE_ROLE_KEY` 하나로 인증이 단순하다.
- ORM 의존성이 없어 서드파티 마이그레이션 도구 없이도 스키마를 직접 관리할 수 있다.

**단점**
- httpx 기반 동기 HTTP 호출로 구현되어 있어 비동기 처리가 필요할 경우 추가 작업이 필요하다.
- 자동화된 쿼리 검증이 없어 런타임 오류가 발생할 때까지 타입 오류를 발견하기 어렵다.
- 테스트에서 실제 Supabase 연결이 필요하거나, Fake 구현을 별도로 유지해야 한다.
- 필터 파라미터(PostgREST 쿼리 문법)가 문자열 기반이라 오타에 취약하다.

### 경로 B — SQLModel + Alembic

**장점**
- 타입이 지정된 ORM 모델로 IDE 자동완성 및 정적 분석이 용이하다.
- SQLite 기반 인메모리/파일 DB로 테스트 격리가 쉽고 빠르다.
- Alembic으로 스키마 변경 이력과 롤백 경로를 관리할 수 있다.
- Repository 패턴으로 쿼리 로직이 모듈화되어 있다.

**단점**
- 운영 환경에서 실제로 사용되지 않으며, Supabase PostgreSQL과 SQLite의 동작 차이로 테스트 신뢰성에 한계가 있다.
- `DATABASE_URL` 환경 변수와 `get_engine`이 필요하나 운영 설정과 무관하여 혼란을 줄 수 있다.
- SQLModel 모델 정의와 Supabase 실제 스키마가 동기화되지 않으면 드리프트가 발생한다.
- 두 가지 경로가 공존하는 한, 새 기능 개발 시 어느 경로를 써야 할지 모호하다.

---

## 4. 현황 요약 (이중 구조 드리프트 현황)

| 항목 | Supabase Data API | SQLModel + Alembic |
|---|---|---|
| 운영 런타임 CRUD | 사용됨 (전체) | 사용 안 됨 |
| 테스트 픽스처 | Fake Store (간접) | 직접 사용 |
| 스키마 정의 출처 | Supabase SQL (외부) | `src/db/models/` |
| 마이그레이션 관리 | Supabase 콘솔/MCP | Alembic (미사용) |
| Enum 공유 | `db.enums` 임포트 | `db.enums` 임포트 |
| 모델 공유 | `PipelineJob.from_job_model` (미호출) | `conftest.py` seed 함수 |

---

## 5. 권장 정리 방향 (PoC 단계 기준)

### 결정: **Supabase Data API를 단일 운영 경로로 유지하되, SQLModel은 테스트 인프라로 존속**

PoC 단계에서 두 경로를 모두 제거하거나 완전 통합하는 리팩터링은 비용 대비 이득이 적다. 다음 방침을 따른다.

#### 즉시 유지할 사항 (현상 유지)

1. **운영 런타임**: 경로 A(Supabase Data API)를 계속 사용한다. 신규 영속성 작업도 동일하다.
2. **`db.enums`**: 두 경로 모두에서 공유하므로 현 위치를 유지한다. 단, enum 변경 시 두 경로 모두에 영향을 확인한다.
3. **Alembic 마이그레이션**: 스키마 이력 참조 문서로 보존한다. 실제 마이그레이션은 Supabase 콘솔/MCP 방식으로 수행한다.
4. **테스트 인프라**: SQLite + SQLModel 기반 Fake Store 패턴을 유지한다. 이는 Supabase 연결 없이 단위/통합 테스트를 빠르게 실행할 수 있는 현실적인 접근법이다.

#### 정리할 사항 (기회가 될 때)

1. **`src/api/dependencies/database.py`**: `get_session`만 재노출하는 파일로, 운영 라우트에서 사용되지 않는다. 테스트 전용 코드임을 주석으로 명시하거나 `tests/conftest.py`로 이동을 검토한다.
2. **`PipelineJob.from_job_model()`**: 운영 코드에서 호출되지 않는 메서드다. 혼란을 방지하기 위해 제거를 검토한다.
3. **`src/db/repositories/`**: 운영 코드에서 미사용 상태다. 테스트 전용 코드임을 명확히 하거나, 테스트 픽스처 내부로 이동하는 것을 장기적으로 검토한다. PoC 단계에서는 현상 유지.

#### 하지 않을 것

- SQLModel 모델을 Supabase 운영 스키마의 "단일 진실 공급원(Source of Truth)"으로 승격시키지 않는다.
- 운영 런타임에 SQLModel Session을 도입하지 않는다.
- 테스트에서 실제 Supabase 연결을 요구하는 구조로 변경하지 않는다.

---

## 6. 마이그레이션 시 고려사항

향후 PoC를 넘어 프로덕션 확장을 준비할 경우:

1. **단일 스키마 소스 결정**: Supabase 콘솔을 스키마 소스로 선택하거나, Alembic을 PostgreSQL에 직접 연결하여 사용하는 방향 중 선택이 필요하다.
2. **테스트 전략 재검토**: Supabase 로컬 에뮬레이터(`supabase start`)를 활용하면 SQLite 기반 Fake Store 없이도 격리 테스트가 가능하다.
3. **비동기 전환**: httpx 동기 클라이언트를 `httpx.AsyncClient`로 교체하거나, `supabase-py` 공식 클라이언트 도입을 검토한다.
4. **스키마 드리프트 감지**: SQLModel 모델(`src/db/models/`)과 실제 Supabase 스키마 간 드리프트가 축적될 수 있으므로, 중요한 스키마 변경 시 두 곳을 동기화하거나 SQLModel 모델을 스키마 참조 문서로 명확히 규정한다.

---

## 7. 결론 및 결정 사항

| 항목 | 결정 |
|---|---|
| 운영 데이터 접근 경로 | Supabase Data API (경로 A) 단독 사용 유지 |
| 신규 영속성 작업 | 경로 A (Supabase Data API)로만 구현 |
| SQLModel + Repository | 테스트 인프라 전용으로 역할 한정 |
| `db.enums` | 공유 상수 모듈로 현 위치 유지 |
| Alembic | 스키마 이력 참조 문서로만 보존 |
| 완전 통합 리팩터링 | PoC 단계에서 보류, 엔드투엔드 루프 안정화 우선 |

이 결정은 현재 PoC 단계에서 낮은 비용으로 코드베이스를 안정적으로 유지하는 방향을 택한 것이다. 엔드투엔드 루프가 완전히 안정화된 이후 단일화 작업을 재검토한다.
