---
plan_id: 2026-04-10-phase5-1-jobkorea-scraper
title: Phase 5-1: Jobkorea 멀티소스 스크래퍼 확장
status: archived
milestone: Phase 5: 스크래퍼/데이터 계층 보강
source_agent: claude
created_at: 2026-04-10T00:00:00+09:00
updated_at: 2026-04-10T16:04:31+09:00
---
# Phase 5-1: Jobkorea 멀티소스 스크래퍼 확장

## 목표

`JobkoreaScraper` 구현 후 `ScraperRegistry`에 등록 → 멀티소스 레지스트리 패턴 검증

**TDD 순서**: 테스트 먼저(Red) → 구현(Green)

## A. 테스트 먼저 작성

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

## B. 구현 파일

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

## C. 검증

```bash
pytest tests/unit/test_jobkorea_scraper.py tests/unit/test_config.py -v
pytest tests/integration/test_jobkorea_ingest.py tests/integration/test_multi_source_ingest.py -v
pytest  # 전체 회귀 없음 확인
```
