# 파이프라인 다중 사용자 확장 설계

**작성일**: 2026-04-10  
**상태**: 설계 문서 (Phase 5-4)  
**대상**: 향후 멀티유저 전환 시 참조

---

## 1. 현재 단일 사용자 가정 목록

현재 PoC는 "단일 사용자"를 전제로 설계되었으나, 코드는 이미 `user_id`를 파라미터로 받아 다중 사용자를 순차 반복하는 골격을 갖추고 있다. 그러나 아래 위치에서 단일 사용자 운영 가정이 명시적 또는 암묵적으로 박혀 있다.

### 1-1. 파이프라인 트리거 — 순차 루프

**파일**: `src/api/services/pipeline_trigger_service.py`, `PipelineTriggerService.trigger()` (L43–L152)

```
users = self._resolve_users(payload)
for user in users:          # 순차 실행 — 사용자 수 증가 시 병목
    graph = build_pipeline_graph(...)
    final_state = await graph.ainvoke(...)
```

- `_resolve_users()`: `payload.user_id`가 없으면 `list_all_users()`로 전체 사용자 조회 후 **한 명씩** 순차 처리.
- 사용자가 10명이면 스크래핑·LLM 평가가 직렬로 10배 소요된다.
- 한 사용자의 스크래핑 실패가 다음 사용자 실행을 지연시킬 수 있다.

### 1-2. AgentState — 단일 사용자 컨텍스트

**파일**: `src/agent/pipeline_state.py`

```python
class AgentState(TypedDict, total=False):
    user_context: Dict[str, Any]   # 단일 사용자의 프로필/필터
    recent_memory: str             # 단일 사용자의 싫어요 요약
    ...
```

`AgentState`는 단일 사용자 컨텍스트만 보유한다. 멀티유저 공유 파이프라인 구조라면 `user_id` 격리가 필요하다.

### 1-3. 각 노드의 user_id 파싱

**파일**: `src/agent/nodes/ingest_node.py` (L30), `rule_filter_node.py` (L112), `llm_eval_node.py` (L39)

```python
user_id = UUID(str(state["user_context"]["user_id"]))
```

모든 노드가 `state["user_context"]["user_id"]`를 직접 파싱한다. 상태가 단일 사용자 dict임을 가정한다.

### 1-4. 스크래퍼 — 사용자 컨텍스트 의존

**파일**: `src/agent/nodes/ingest_node.py` (L36)

```python
scraped_jobs = await source.fetch_jobs(state["user_context"])
```

`IngestNode`가 스크래퍼에 `user_context` 전체를 넘긴다. 스크래퍼가 사용자별 필터(예: 키워드)로 검색 쿼리를 구성하면, 공유 스크래핑 결과를 캐싱하거나 재활용하기 어렵다.

### 1-5. RuntimeServices — 전역 싱글턴

**파일**: `src/api/services/runtime.py`

```python
@dataclass(frozen=True)
class RuntimeServices:
    scraper_registry: ScraperRegistry
    llm_evaluator: Any
    prompt_manager: PromptManager
    slack_notifier: LoggingSlackNotifier
    langsmith_tracer: LangSmithTracer
```

현재 `RuntimeServices`는 앱 기동 시 1개 인스턴스로 고정된다. `slack_notifier`가 단일 Slack 채널/웹훅을 가정하고 있어, 사용자별 Slack 채널 라우팅이 불가능하다.

### 1-6. Slack 알림 — 단일 웹훅/채널

**파일**: `src/api/services/slack_notifier.py` (LoggingSlackNotifier), `src/common/config.py` (`SLACK_WEBHOOK_URL`, `SLACK_ALERTS_CHANNEL`)

알림 설정이 앱 전역 환경 변수 1개로 관리된다. 사용자별 Slack DM 또는 채널이 필요하면 `notification_settings`에 웹훅 URL이나 채널 ID를 추가해야 한다.

### 1-7. 스케줄러 트리거 — GitHub Actions 단일 cron

**파일**: `.github/workflows/ci.yml` (현재 CI만 존재, 별도 스케줄 워크플로우 없음)

현재는 `POST /api/v1/pipeline/trigger`를 외부에서 수동 또는 단순 cron으로 호출하는 구조다. 사용자별 실행 주기나 시간대(timezone) 설정이 없다.

### 1-8. 설정 — 사용자별 분리 없음

**파일**: `src/common/config.py`

`Settings`는 전역 스칼라 값 집합이다. `SCRAPER_MAX_PAGES`, `GEMINI_MODEL` 등 성능 민감 파라미터가 사용자별로 다를 수 없다.

---

## 2. 멀티유저 전환 시 필요한 변경사항 (우선순위별)

### 우선순위 1 — 정확성·격리 (필수)

| 변경 항목 | 현재 문제 | 필요 조치 |
|-----------|-----------|-----------|
| **평가 격리** | 모든 evaluation 레코드에 `user_id`가 이미 포함됨 (이미 OK) | 추가 변경 없음, 기존 스키마 유지 |
| **Job 중복 제거** | `jobs` 테이블이 플랫폼+external_job_id 기준 글로벌 공유 — 사용자 간 동일 공고 공유 | 공고 자체는 공유 유지, `evaluation`으로 사용자별 처리 상태 관리 (현재 설계 유지 가능) |
| **싫어요 메모리 격리** | `list_recent_dislikes(user_id, ...)` 이미 user_id 필터링 | 추가 변경 없음 |
| **Slack 채널 라우팅** | 글로벌 SLACK_WEBHOOK_URL 1개 | `users.notification_settings`에 `slack_webhook_url` 필드 추가 필요 |

### 우선순위 2 — 성능·확장성 (중요)

| 변경 항목 | 현재 문제 | 필요 조치 |
|-----------|-----------|-----------|
| **병렬 파이프라인 실행** | 사용자별 순차 실행으로 N배 지연 | `asyncio.gather()` 또는 작업 큐(Celery/ARQ)로 병렬화 |
| **스크래핑 캐싱** | 사용자별로 동일 플랫폼을 중복 스크래핑 | 플랫폼별 공유 스크래핑 결과를 TTL 캐시로 관리 후 사용자별 필터 적용 |
| **LLM 비용** | 사용자 N명에 비례해 LLM 호출 N배 | 동일 공고에 대해 사용자 프로필이 유사하면 배치 평가 고려 |

### 우선순위 3 — 운영·관리 (권장)

| 변경 항목 | 현재 문제 | 필요 조치 |
|-----------|-----------|-----------|
| **사용자별 스케줄링** | 단일 cron으로 전체 실행 | 사용자별 preferred_time, timezone 지원 |
| **사용자별 scraper 파라미터** | SCRAPER_MAX_PAGES 글로벌 고정 | `user.preferences`에 페이지 수 등 오버라이드 허용 |
| **사용자별 모델 선택** | GEMINI_MODEL 글로벌 고정 | 프리미엄 사용자에 고성능 모델 라우팅 가능 구조 |
| **관리자 UI** | `/internal`에 단일 사용자 뷰 | 사용자 목록, 실행 이력, 오류 집계 뷰 추가 |

---

## 3. 설계 옵션 비교

### 옵션 A: 사용자별 독립 파이프라인 인스턴스

각 사용자 실행마다 완전히 독립된 LangGraph 그래프와 노드 인스턴스를 생성한다. 현재 구조의 확장.

```
trigger → [for each user]
  └─ build_pipeline_graph()
  └─ IngestNode (사용자 컨텍스트로 스크래핑)
  └─ RuleFilterNode
  └─ LLMEvalNode
  └─ DeliverNode
```

**장점**:
- 사용자 간 상태 완전 격리 — 버그 영향 범위 제한
- 현재 코드 변경 최소 (병렬화만 추가)
- 사용자별 스크래핑 키워드로 타깃 공고 수집 가능

**단점**:
- 동일 플랫폼을 사용자 수 × N번 스크래핑 → Playwright 리소스 부하
- 동일 공고를 사용자별로 중복 LLM 평가 → 비용 선형 증가
- 사용자 100명이면 Playwright 100개 병렬 실행 불가

**적합한 규모**: 10명 이하 소규모 멀티유저

---

### 옵션 B: 공유 파이프라인 + 사용자 컨텍스트 주입

플랫폼별 스크래핑을 1회 실행하여 전체 공고 풀을 확보한 뒤, 사용자별 필터링·평가를 팬아웃(fan-out)한다.

```
trigger
  └─ SharedIngestPhase (플랫폼별 1회 스크래핑)
       └─ [for each user] UserEvalPhase
              └─ RuleFilterNode (user_context 주입)
              └─ LLMEvalNode (user_context 주입)
              └─ DeliverNode (user_context 주입)
```

**장점**:
- 스크래핑 비용 O(플랫폼 수) — 사용자 수 무관
- Playwright 인스턴스 최소화
- 동일 공고에 대한 스크래핑 중복 없음

**단점**:
- 사용자별 검색 키워드가 다르면 공유 공고 풀로 모든 사용자를 커버할 수 없음
- 현재 `IngestNode`가 `user_context`로 스크래핑 쿼리를 구성하는 구조라면 리팩토링 필요
- 공유 공고 풀 크기 결정이 어려움 (너무 넓으면 필터 부하, 너무 좁으면 누락)
- `AgentState` 설계 변경 필요 — 현재 단일 user_context 구조 탈피

**적합한 규모**: 10명 이상, 직군이 유사한 사용자 집합

---

### 권고 전략

| 단계 | 규모 | 전략 |
|------|------|------|
| PoC → 초기 확장 | ~10명 | 옵션 A + `asyncio.gather()` 병렬화 |
| 성장기 | 10~50명 | 옵션 B (공유 스크래핑) + 사용자별 LLM 평가 병렬화 |
| 프로덕션 | 50명+ | 옵션 B + 작업 큐(ARQ/Celery) + 수평 확장 워커 |

**PoC에서 초기 확장으로 가는 최소 변경**: 옵션 A에서 `asyncio.gather()` 적용 + Slack 웹훅 사용자별 라우팅.

---

## 4. 데이터 모델 변경 필요 사항

### 현재 스키마 (Supabase)

```
users        — id, email, oauth_id, profile_data, guidelines, preferences, notification_settings
jobs         — id, platform, external_job_id, title, company, jd_raw_text, url, ...
evaluations  — id, user_id, job_id, status, fit_score, reasoning, user_feedback, ...
system_logs  — id, run_id, event_type, level, message, user_id, job_id, platform, metadata
```

### 필요한 변경

#### 4-1. `users.notification_settings` 필드 확장

현재 `minimum_fit_score`, `delivery_channel`만 있음. 멀티유저에서 필요한 추가 필드:

```json
{
  "minimum_fit_score": 80,
  "delivery_channel": "slack",
  "slack_webhook_url": "https://hooks.slack.com/...",  // 사용자별 웹훅 (신규)
  "slack_channel_id": "D012345",                        // DM 채널 ID (신규)
  "preferred_run_time": "09:00",                        // 실행 희망 시간 (신규, 옵션)
  "timezone": "Asia/Seoul"                              // 타임존 (신규, 옵션)
}
```

#### 4-2. `pipeline_runs` 테이블 (신규 권장)

현재 파이프라인 실행 결과가 `system_logs`에 이벤트로만 기록된다. 멀티유저에서는 실행 단위 집계가 필요하다:

```sql
CREATE TABLE pipeline_runs (
    id          UUID PRIMARY KEY,
    run_id      TEXT NOT NULL,
    user_id     UUID REFERENCES users(id),
    started_at  TIMESTAMPTZ NOT NULL,
    completed_at TIMESTAMPTZ,
    status      TEXT,           -- running, completed, failed
    jobs_ingested INT,
    jobs_evaluated INT,
    jobs_sent   INT,
    source_errors JSONB,
    metadata    JSONB
);
```

#### 4-3. `jobs` 테이블 — 변경 없음

`jobs`는 플랫폼+external_job_id 기준 글로벌 공유 테이블로 유지한다. 사용자별 처리 상태는 `evaluations`로 관리하는 현재 설계가 옳다.

#### 4-4. `users.preferences` 필드 확장 (선택)

사용자별 스크래퍼 파라미터 오버라이드가 필요한 경우:

```json
{
  "scraper_max_pages": 3,    // 글로벌 기본값 오버라이드
  "scraper_platforms": ["incruit", "wanted"]  // 활성화할 플랫폼 목록
}
```

---

## 5. 스케줄링 변경 필요 사항

### 현재 구조

- 외부(GitHub Actions 또는 수동)에서 `POST /api/v1/pipeline/trigger`를 `X-API-Key`로 호출
- `payload.user_id`가 없으면 전체 사용자 실행
- 스케줄 실행은 `PIPELINE_ENABLED=true` + `APP_ENV=production`에서만 허용

### 멀티유저 스케줄링 옵션

#### 옵션 S1: 단일 cron + 전체 사용자 팬아웃 (현재 구조 유지)

```yaml
# GitHub Actions (매일 오전 9시 KST)
schedule:
  - cron: '0 0 * * *'    # UTC 00:00 = KST 09:00
```

- `trigger(user_id=None)` → 전체 사용자 실행
- 장점: 인프라 변경 없음
- 단점: 사용자별 시간대·선호 실행 시간 미지원

#### 옵션 S2: 사용자별 cron (GitHub Actions matrix)

```yaml
strategy:
  matrix:
    user_id: [uuid-1, uuid-2, ...]
steps:
  - run: curl -X POST .../trigger -d '{"user_id": "${{ matrix.user_id }}"}'
```

- 장점: 사용자별 독립 실행, 실패 격리
- 단점: 사용자 추가/삭제 시 워크플로우 수정 필요

#### 옵션 S3: 내부 스케줄러 (권장, 장기)

`APScheduler` 또는 `ARQ`를 FastAPI 앱 내부에 통합하여 사용자별 스케줄을 DB에서 관리한다.

```python
# 개념적 구조
for user in users:
    schedule = user.notification_settings.get("preferred_run_time")
    scheduler.add_job(run_pipeline_for_user, trigger='cron', args=[user.user_id], ...)
```

- 장점: 사용자별 시간대, 실행 주기 유연 관리
- 단점: 인프라 복잡도 증가, 별도 워커 프로세스 필요

**단기 권고**: 옵션 S1 유지 + `asyncio.gather()` 병렬화  
**중기 권고**: 옵션 S3으로 전환

---

## 6. PoC에서 프로덕션으로의 전환 로드맵

### Phase 1: PoC 안정화 (현재)

- 단일 사용자 엔드투엔드 루프 완성
- LangSmith 트레이싱, 피드백 루프, 프롬프트 거버넌스 구축
- **목표**: 파이프라인 품질 검증 및 운영 관행 확립

### Phase 2: 소규모 멀티유저 (2~10명, 최소 변경)

**필요 변경 (코드)**:
1. `PipelineTriggerService.trigger()` — `asyncio.gather()` 병렬화 (단, Playwright 동시 실행 수 제한 필요)
2. `notification_settings`에 `slack_webhook_url` 필드 추가
3. `DeliverNode` — `user_context`에서 사용자별 webhook URL 읽어 Slack 전송

**필요 변경 (인프라)**:
- Supabase: `users.notification_settings` 스키마 업데이트
- 환경 변수: `PIPELINE_MAX_CONCURRENT_USERS` 추가 (Playwright 과부하 방지)

**예상 공수**: 1~2일

### Phase 3: 중규모 확장 (10~50명)

**필요 변경**:
1. 공유 스크래핑 캐시 (옵션 B 전환)
   - `IngestNode`를 사용자 컨텍스트에서 분리
   - 플랫폼별 공통 공고 풀 확보 후 사용자 팬아웃
2. `pipeline_runs` 테이블 신설
3. `/internal` 대시보드에 사용자별 실행 이력 집계 뷰 추가
4. Playwright 워커 풀 관리 (`asyncio.Semaphore` 또는 별도 프로세스)

**예상 공수**: 1~2주

### Phase 4: 프로덕션 수평 확장 (50명+)

**필요 변경**:
1. 작업 큐 도입 (ARQ/Celery + Redis)
   - 파이프라인 실행 작업을 메시지로 발행
   - 워커 프로세스 수평 확장
2. 내부 스케줄러 (옵션 S3)
3. 사용자별 rate limiting (LLM API 키 쿼터 관리)
4. 멀티테넌트 LangSmith 트레이싱 (사용자별 프로젝트 또는 태그)
5. 모니터링 강화: 사용자별 파이프라인 지연, 오류율 대시보드

**예상 공수**: 2~4주 (팀 규모에 따라 다름)

---

## 7. 브레이킹 체인지 주의 사항

멀티유저 전환 시 아래 항목은 하위 호환을 검토해야 한다:

1. **`notification_settings` 스키마 변경**: 기존 사용자의 `notification_settings` JSON에 신규 필드를 추가할 때 `None` 기본값 처리 필요. `UserProfileResponse` 모델 업데이트 시 `src/api/schemas/users.py`와 DB 동기화 필수.

2. **`pipeline_runs` 신설**: `system_logs`의 `pipeline_started`/`pipeline_completed` 이벤트와 중복 가능성. 마이그레이션 시 기존 로그와의 관계 명확화 필요.

3. **`IngestNode`의 `user_context` 의존 제거 (옵션 B)**: 현재 스크래퍼 구현(`IncruitScraper`)이 `user_context`로 검색 쿼리를 구성하는지 확인 후 인터페이스 변경. `BaseScraperSource.fetch_jobs()` 시그니처 변경은 모든 스크래퍼 구현에 영향.

4. **`LangSmithTracer.pipeline_run()` 컨텍스트**: 현재 `user_id`가 LangSmith 메타데이터로 기록됨. 병렬 실행 시 트레이스 컨텍스트가 스레드/태스크 간 오염되지 않는지 확인 필요.

---

## 참고 파일 경로

| 파일 | 역할 |
|------|------|
| `src/agent/pipeline_state.py` | `AgentState` 정의 |
| `src/agent/workflow.py` | LangGraph 그래프 빌드 |
| `src/agent/nodes/ingest_node.py` | 스크래핑 노드 |
| `src/agent/nodes/rule_filter_node.py` | 규칙 필터 노드 |
| `src/agent/nodes/llm_eval_node.py` | LLM 평가 노드 |
| `src/agent/nodes/deliver_node.py` | 전달 노드 |
| `src/api/routes/pipeline.py` | 트리거 엔드포인트 |
| `src/api/services/pipeline_trigger_service.py` | 트리거 서비스 (루프 위치) |
| `src/api/services/runtime.py` | RuntimeServices 싱글턴 |
| `src/api/services/slack_notifier.py` | Slack 전송 (현재 글로벌) |
| `src/api/services/supabase_storage.py` | 모든 Supabase 스토어 |
| `src/common/config.py` | 전역 설정 (사용자별 오버라이드 없음) |
