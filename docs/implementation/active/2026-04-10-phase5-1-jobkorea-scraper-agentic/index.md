---
plan_id: 2026-04-10-phase5-1-jobkorea-scraper-agentic
title: Phase 5-1: Jobkorea 스크래퍼 (Agentic TDD)
status: reference
milestone: Phase 5: 스크래퍼/데이터 계층 보강
source_agent: claude
created_at: 2026-04-10T00:00:00+09:00
updated_at: 2026-04-10T00:00:00+09:00
---

# Phase 5-1: Jobkorea 스크래퍼 (Agentic TDD)

## 목표

`JobkoreaScraper` 구현 후 `ScraperRegistry`에 등록 → 멀티소스 레지스트리 패턴 검증.
하네스(worktree, branch guard, Codex plan review hook)가 실제 기능 구현에서 동작하는 첫 번째 Agentic Engineering 사례.

현재 harness + agent 전환 기준에서는 이 plan을 `Phase 4: PromptOps 에이전트 분석 루프` 다음의 실전 적용 단계로 해석한다. 즉, 이 작업의 핵심 가치는 scraper 기능 추가 자체보다, 앞선 agent loop와 하네스를 실제 제품 코드 변경과 integration 검증에 연결해보는 데 있다.

상위 방향 문서: [Existing Harness to Agentic Engineering Migration Plan](../2026-04-10-agentic-engineering-migration-plan/index.md)

## 에이전트 실행 프로토콜

| 단계 | 에이전트 | 작업 | 검증 기준 |
|------|---------|------|----------|
| 1 | **[Human]** | `scripts/start_agent_task.sh --agent codex --task jobkorea-scraper` 실행 | worktree 생성 확인 |
| 2 | **[Codex]** | Red: 테스트 파일 3개 작성 (아래 A 섹션) | `pytest tests/unit/test_jobkorea_scraper.py -v` → 전부 FAILED |
| 3 | **[Codex]** | Green: 구현 파일 작성 (아래 B 섹션) | `pytest tests/unit/test_jobkorea_scraper.py tests/integration/ -v` → 전부 PASSED |
| 4 | **[Codex]** | PR: `codex/jobkorea-scraper` → `main` | PR 생성 후 Codex plan review hook 통과 |
| 5 | **[Human]** | `scripts/start_integration_task.sh --task jobkorea-scraper` 실행 | worktree 생성 확인 |
| 6 | **[Claude]** | integration worktree에서 멀티소스 회귀 확인 | `pytest` 전체 통과 + 멀티소스 ingest 수동 smoke test |
| 7 | **[Human]** | main merge 최종 승인 | |

## A. 테스트 먼저 작성 (Codex: Red 단계)

### `tests/unit/test_jobkorea_scraper.py` — 파서 단위 테스트 8개

- `test_build_search_url_includes_keyword_and_page` (URL: `stext=<kw>&Page_No=<page>`)
- `test_parse_listing_page_extracts_multiple_cards` (`div.recruit-info[data-gno]` 카드 2개)
- `test_parse_listing_page_extracts_real_jobkorea_card_shape` (`li.post-list[data-gno]` 실제 DOM 형태)
- `test_parse_detail_page_extracts_job_description_and_identifier` (`div.view-cont` + `/Recruit/GI_Read/12345` → ID)
- `test_parse_detail_page_prefers_job_posting_json_ld_when_available`
- `test_extract_external_job_id_uses_path_and_hint_fallbacks`
- `test_normalize_scraped_job_builds_absolute_urls_and_rejects_short_jd`
- `test_parse_experience_years_wiring` (incruit parsers import 확인)

### `tests/unit/test_config.py` 추가

- `test_settings_reject_empty_jobkorea_base_url`

### `tests/integration/test_jobkorea_ingest.py` — `FixtureJobkoreaScraper` (Playwright 우회)

- `test_jobkorea_ingest_upserts_jobs_and_discards_invalid_entries`
- `test_jobkorea_scraper_partial_parse_failure_does_not_fail_source`

### `tests/integration/test_multi_source_ingest.py` — **핵심: 레지스트리 패턴 검증**

- `test_ingest_node_collects_jobs_from_both_sources` (양 플랫폼 공고 모두 포함)
- `test_ingest_node_continues_when_jobkorea_fails_but_incruit_succeeds`
- `test_ingest_node_continues_when_incruit_fails_but_jobkorea_succeeds`
  > `FailingScraper` source_name은 conftest 수정 없이 테스트 내 로컬 클래스로 처리

## B. 구현 파일 (Codex: Green 단계)

- `src/scraper/sources/jobkorea/selectors.py`
  - `SOURCE_NAME = "jobkorea"`, `DEFAULT_BASE_URL = "https://www.jobkorea.co.kr"`
  - `build_search_url(*, base_url, keyword, page)` — params: `stext`, `Page_No`
  - `LISTING_CARD_HINTS`, `DETAIL_HINTS`, `DETAIL_ID_QUERY_KEYS = ["gno", "gi_no"]`
- `src/scraper/sources/jobkorea/parsers.py`
  - `_ListingParser`: `data-gno` 우선 (external_hint), href fallback
  - `parse_detail_page`: `div.view-cont` / `div#workerRecDetail` JD 추출, JSON-LD 우선
  - `extract_external_job_id`: path `/Recruit/GI_Read/<id>` → numeric ID
  - `parse_experience_years`: **`incruit/parsers.py`에서 import** (복사 금지)
- `src/scraper/sources/jobkorea/scraper.py` — `IncruitScraper` 구조 동일
  - `wait_until="networkidle"` (Jobkorea JS-heavy; Incruit은 domcontentloaded)
  - `_derive_keywords`: Incruit과 동일 로직 (추상화 YAGNI)
- `src/scraper/sources/jobkorea/__init__.py`
- `src/common/config.py` — `scraper_jobkorea_base_url` 필드 + `validate_environment` 검증 추가
- `src/api/services/runtime.py` — `ScraperRegistry([IncruitScraper(...), JobkoreaScraper(...)])` 등록
- `.env.example` — `SCRAPER_JOBKOREA_BASE_URL=https://www.jobkorea.co.kr` 추가

## C. 검증 커맨드 (Codex 자율 실행)

```bash
# Red 단계 확인
pytest tests/unit/test_jobkorea_scraper.py tests/unit/test_config.py -v
# → 전부 FAILED 확인 후 구현 시작

# Green 단계 확인
pytest tests/unit/test_jobkorea_scraper.py tests/unit/test_config.py -v
pytest tests/integration/test_jobkorea_ingest.py tests/integration/test_multi_source_ingest.py -v
pytest  # 전체 회귀 없음 확인
```

## 참조 파일

- `src/scraper/sources/incruit/` — 구현 패턴 참조 (selectors, parsers, scraper)
- `src/scraper/base.py` — `BaseScraperSource` 프로토콜, `ScrapedJob` 모델
- `src/scraper/registry.py` — `ScraperRegistry`
- `src/scraper/normalizers/job_normalizer.py` — 정규화 로직 재사용
- `src/api/services/runtime.py` — 현재 스크래퍼 등록 방식
- `src/common/config.py` — 설정 패턴
- `tests/unit/test_incruit_scraper.py` — 테스트 패턴 참조
- `tests/integration/test_incruit_ingest.py` — 통합 테스트 패턴 참조
