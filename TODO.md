# TODO.md

이 문서는 하네스 엔지니어링 리스트럭처링의 실행 단위별 작업 목록입니다.
MILESTONE.md가 장기 진화를, 이 파일은 단기 실행을 추적합니다.

생성일: 2026-04-09

---

## Phase 0: 사전 작업

- [ ] `poetry install` 실행하여 백엔드 의존성 정상화
- [ ] `cd apps/web && npm ci` 실행하여 프론트엔드 의존성 정상화
- [ ] `poetry run pytest tests/unit -x -q` 실행하여 테스트 기준선 확인
- [ ] `cd apps/web && npx tsc --noEmit` 실행하여 TypeScript 에러 확인

---

## Phase 1: 하네스 엔지니어링 기반 구축

### 1-1. .claude/rules/ 규칙 파일 생성
AGENTS.md의 도메인별 섹션을 개별 파일로 추출.

- [ ] `.claude/rules/architecture.md` -- 폴더 구조, 모듈 설계, 아키텍처 규칙 (AGENTS.md L79-135)
- [ ] `.claude/rules/pipeline.md` -- LangGraph 워크플로우, 데이터 모델, 평가 수명주기 (L145-187)
- [ ] `.claude/rules/scraper.md` -- 스크래퍼 프로토콜, 소스 격리, 레지스트리 패턴
- [ ] `.claude/rules/promptops.md` -- 프롬프트 관리, 실험 플로우, CLI, 에이전트 워크플로우
- [ ] `.claude/rules/frontend.md` -- Next.js 규칙, 컴포넌트 구조, Supabase SSR, PoC 범위
- [ ] `.claude/rules/testing.md` -- 테스트 우선순위, 형태 지침, 완료 조건 (L291-341)
- [ ] `.claude/rules/api-contracts.md` -- 엔드포인트, 인증 경계, API 변경 규칙 (L137-213)
- [ ] `.claude/rules/config-env.md` -- 환경 분리, 명명 규칙, 시크릿 처리 (L64-245)

### 1-2. CLAUDE.md 생성
- [ ] 프로젝트 루트에 CLAUDE.md 생성 (경로 참조 스타일, 인라인 최소화)

### 1-3. AGENTS.md 리팩터링
- [ ] 378줄 → ~120줄로 슬림화 (추출된 섹션을 규칙 파일 참조로 대체)

### 1-4. .claude/settings.json 생성
- [ ] PreCommit 훅 (tsc + pytest)
- [ ] PostCommit 훅 (status.md 업데이트 리마인더)
- [ ] 권한 설정

---

## Phase 2: 문서 고도화 및 추적 체계

### 2-1. MILESTONE.md
- [x] 프로젝트 루트에 MILESTONE.md 생성 (Phase 0~4 진화 이력)

### 2-2. 세션 히스토리
- [x] `.claude/sessions/` 디렉토리 생성
- [x] 세션 로그 템플릿 파일 생성
- [x] `.gitignore`에 `.claude/sessions/` 추가

### 2-3. 첫 세션 기록
- [x] 이번 세션(하네스 리스트럭처링 계획) 기록 작성

---

## Phase 3: CI/CD 및 코드 품질

### 3-1. 린터 설정
- [x] `pyproject.toml`에 ruff dev 의존성 추가
- [x] `[tool.ruff]` 설정 추가
- [x] `ruff check --fix` 첫 실행으로 자동 수정 가능한 이슈 처리
- [x] `ruff format` 첫 실행으로 포맷팅 정리
- [x] pre-existing 버그 수정 (eval_type_backport 추가, 테스트 fixture 동기화)

### 3-2. GitHub Actions
- [x] `.github/workflows/ci.yml` 생성
  - backend job: ruff lint → ruff format check → pytest unit → pytest contract
  - frontend job: npm ci → tsc --noEmit → vitest run

---

## Phase 4: PromptOps 에이전트 통합

### 4-1. 에이전트 워크플로우 규칙
- [ ] `.claude/rules/promptops.md`에 에이전트 워크플로우 섹션 추가

### 4-2. 통합 포인트 구현
- [ ] 실험 후 분석 워크플로우 (iteration 리포트 → 실패 패턴 그룹화 → 트렌드 감지)
- [ ] 실패 패턴 트렌드 리포트 생성
- [ ] Borderline 케이스 데이터셋 큐레이션 워크플로우
- [ ] 프롬프트 최적화 제안 자동화
- [ ] 규칙 필터 개선 분석

---

## Phase 5: 이전 평가 개선 포인트

### 5-1. 스크래퍼 확장 (JobkoreaScraper)

**목표**: `JobkoreaScraper` 구현 후 `ScraperRegistry`에 등록 → 멀티소스 레지스트리 패턴 검증
**TDD 순서**: 테스트 먼저(Red) → 구현(Green)

#### A. 테스트 먼저 작성
- [ ] `tests/unit/test_jobkorea_scraper.py` — 파서 단위 테스트 8개
  - `test_build_search_url_includes_keyword_and_page` (URL: `stext=<kw>&Page_No=<page>`)
  - `test_parse_listing_page_extracts_multiple_cards` (`div.recruit-info[data-gno]` 카드 2개)
  - `test_parse_listing_page_extracts_real_jobkorea_card_shape` (`li.post-list[data-gno]` 실제 DOM 형태)
  - `test_parse_detail_page_extracts_job_description_and_identifier` (`div.view-cont` + `/Recruit/GI_Read/12345` → ID)
  - `test_parse_detail_page_prefers_job_posting_json_ld_when_available`
  - `test_extract_external_job_id_uses_path_and_hint_fallbacks`
  - `test_normalize_scraped_job_builds_absolute_urls_and_rejects_short_jd`
  - `test_parse_experience_years_wiring` (incruit parsers import 확인)
- [ ] `tests/unit/test_config.py` — `test_settings_reject_empty_jobkorea_base_url`
- [ ] `tests/integration/test_jobkorea_ingest.py` — `FixtureJobkoreaScraper` (Playwright 우회)
  - `test_jobkorea_ingest_upserts_jobs_and_discards_invalid_entries`
  - `test_jobkorea_scraper_partial_parse_failure_does_not_fail_source`
- [ ] `tests/integration/test_multi_source_ingest.py` — **핵심: 레지스트리 패턴 검증**
  - `test_ingest_node_collects_jobs_from_both_sources` (양 플랫폼 공고 모두 포함)
  - `test_ingest_node_continues_when_jobkorea_fails_but_incruit_succeeds`
  - `test_ingest_node_continues_when_incruit_fails_but_jobkorea_succeeds`
  > `FailingScraper` source_name은 conftest 수정 없이 테스트 내 로컬 클래스로 처리

#### B. 구현
- [ ] `src/scraper/sources/jobkorea/selectors.py`
  - `SOURCE_NAME = "jobkorea"`, `DEFAULT_BASE_URL = "https://www.jobkorea.co.kr"`
  - `build_search_url(*, base_url, keyword, page)` — params: `stext`, `Page_No`
  - `LISTING_CARD_HINTS`, `DETAIL_HINTS`, `DETAIL_ID_QUERY_KEYS = ["gno", "gi_no"]`
- [ ] `src/scraper/sources/jobkorea/parsers.py`
  - `_ListingParser`: `data-gno` 우선 (external_hint), href fallback
  - `parse_detail_page`: `div.view-cont` / `div#workerRecDetail` JD 추출, JSON-LD 우선
  - `extract_external_job_id`: path `/Recruit/GI_Read/<id>` → numeric ID
  - `parse_experience_years`: **`incruit/parsers.py`에서 import** (복사 금지)
- [ ] `src/scraper/sources/jobkorea/scraper.py` — `IncruitScraper` 구조 동일
  - `wait_until="networkidle"` (Jobkorea JS-heavy; Incruit은 domcontentloaded)
  - `_derive_keywords`: Incruit과 동일 로직 복사 (추상화 YAGNI)
- [ ] `src/scraper/sources/jobkorea/__init__.py`
- [ ] `src/common/config.py` — `scraper_jobkorea_base_url` 필드 + `validate_environment` 검증 추가
- [ ] `src/api/services/runtime.py` — `ScraperRegistry([IncruitScraper(...), JobkoreaScraper(...)])` 등록
- [ ] `.env.example` — `SCRAPER_JOBKOREA_BASE_URL=https://www.jobkorea.co.kr` 추가

#### 검증
```bash
pytest tests/unit/test_jobkorea_scraper.py tests/unit/test_config.py -v
pytest tests/integration/test_jobkorea_ingest.py tests/integration/test_multi_source_ingest.py -v
pytest  # 전체 회귀 없음 확인
```

### 5-2. 데이터 접근 계층 정리
- [x] Supabase Data API vs SQLModel 이중 구조 정리 방향 결정 문서 작성

### 5-3. 프론트엔드 경량화
- [x] Three.js / Framer Motion 의존성 제거 검토 및 실행

### 5-4. 멀티유저 확장 설계
- [x] 파이프라인 다중 사용자 확장 설계 문서 작성
