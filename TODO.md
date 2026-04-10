# TODO.md

이 문서는 하네스 엔지니어링 전환 이후의 단기 실행 보드(canonical short-term execution board)입니다.
상세한 분석과 우선순위 배경은 [docs/implementation/harness_engineering_transition_gap_plan.md](docs/implementation/harness_engineering_transition_gap_plan.md)를 참조하세요.

생성일: 2026-04-09

---

## Phase 0: 기준선 검증 결과

- [x] `poetry run pytest tests/unit -q` 기준선 확인 완료 (`59 passed`)
- [x] `cd apps/web && npm run typecheck` 기준선 확인 완료 (pass)
- [x] `cd apps/web && npm run test` 기준선 확인 완료 (현재 fail 5건 기록)

---

## Phase 1: 하네스 전환 문서화 정리

- [x] `docs/implementation/harness_engineering_transition_gap_plan.md` 생성
- [x] `.claude/rules/architecture.md` 생성
- [x] `.claude/rules/pipeline.md` 생성
- [x] `.claude/rules/scraper.md` 생성
- [x] `.claude/rules/promptops.md` 생성
- [x] `.claude/rules/frontend.md` 생성
- [x] `.claude/rules/testing.md` 생성
- [x] `.claude/rules/api-contracts.md` 생성
- [x] `.claude/rules/config-env.md` 생성
- [x] 프로젝트 루트 `CLAUDE.md` 생성
- [x] `AGENTS.md` 슬림화 완료
- [x] `.claude/settings.json` 생성
- [x] `MILESTONE.md` 생성
- [x] `.github/workflows/ci.yml` 생성
- [x] `pyproject.toml` 내 `ruff` 설정 반영
- [x] `.claude/rules/promptops.md`에 에이전트 워크플로우 규칙 반영

---

## Phase 2: 프론트엔드 계약 안정화

- [ ] `apps/web` 대시보드 테스트 mock을 현재 `preferences` 계약에 맞게 정리
- [ ] `apps/web` 내부 운영 허브 테스트 mock을 현재 `internalStatus` shape에 맞게 정리
- [ ] `apps/web` PromptOps 문서 파서 테스트를 현재 문서 구조 기준으로 보강
- [ ] `cd apps/web && npm run test` 실패 5건을 복구할 구현/테스트 패치 진행

---

## Phase 3: 운영 hygiene 정리

- [ ] `.claude/sessions/` 디렉토리 생성
- [ ] 세션 로그 템플릿 파일 생성
- [x] `.gitignore`에 `.claude/sessions/` ignore 규칙 반영
- [ ] `.claude/worktrees/`를 로컬 병렬 작업 산출물로 관리하는 규칙을 문서/ignore 정책에 반영
- [ ] 루트 저장소와 worktree의 역할 분리를 운영 문서에 명시

---

## Phase 4: PromptOps 자동화 확장

- [ ] 실험 후 분석 워크플로우 (iteration 리포트 → 실패 패턴 그룹화 → 트렌드 감지)
- [ ] 실패 패턴 트렌드 리포트 생성
- [ ] Borderline 케이스 데이터셋 큐레이션 워크플로우
- [ ] 프롬프트 최적화 제안 자동화
- [ ] 규칙 필터 개선 분석

---

## Phase 5: 멀티소스 확장 및 후속 기능

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
