from __future__ import annotations

from typing import Any, Dict, List, Optional

from common.logging import get_logger
from scraper.base import ScrapedJob
from scraper.normalizers.job_normalizer import InvalidScrapedJobError, normalize_scraped_job
from scraper.sources.incruit.parsers import (
    extract_external_job_id,
    parse_detail_page,
    parse_experience_years,
    parse_listing_page,
)
from scraper.sources.incruit.selectors import DEFAULT_BASE_URL, SOURCE_NAME, build_search_url


logger = get_logger(__name__)


class IncruitScraper:
    source_name = SOURCE_NAME

    def __init__(
        self,
        *,
        headless: bool = True,
        timeout_ms: int = 15000,
        max_pages: int = 2,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.max_pages = max_pages
        self.base_url = base_url.rstrip("/")

    async def fetch_jobs(self, user_context: Dict[str, Any]) -> List[ScrapedJob]:
        jobs: List[ScrapedJob] = []
        seen_keys: set[str] = set()
        discarded_jobs = 0
        fetched_listing_count = 0
        page_count = 0
        searched_keywords = self._derive_keywords(user_context)

        for keyword in searched_keywords:
            for page in range(1, self.max_pages + 1):
                page_count += 1
                listing_html = await self._fetch_search_html(keyword=keyword, page=page)
                previews = parse_listing_page(listing_html)
                fetched_listing_count += len(previews)

                for preview in previews:
                    try:
                        detail_html = await self._fetch_detail_html(preview.detail_url)
                        detail = parse_detail_page(
                            detail_html,
                            detail_url=preview.detail_url,
                            hint=preview.external_hint,
                        )
                        external_job_id = detail.external_job_id or extract_external_job_id(
                            detail_url=preview.detail_url,
                            hint=preview.external_hint,
                        )
                        unique_key = external_job_id or preview.detail_url
                        if unique_key in seen_keys:
                            continue

                        min_years_experience, max_years_experience = parse_experience_years(
                            detail.experience_text or preview.experience_text
                        )

                        candidate = normalize_scraped_job(
                            ScrapedJob(
                                platform=self.source_name,
                                external_job_id=external_job_id,
                                title=preview.title,
                                company=preview.company,
                                jd_raw_text=detail.jd_raw_text,
                                url=detail.canonical_url or preview.detail_url,
                                min_years_experience=min_years_experience,
                                max_years_experience=max_years_experience,
                                source_metadata={
                                    "base_url": self.base_url,
                                    "search_keyword": keyword,
                                    "page": page,
                                    "experience_text": detail.experience_text or preview.experience_text,
                                },
                            )
                        )
                        jobs.append(candidate)
                        seen_keys.add(unique_key)
                    except InvalidScrapedJobError as exc:
                        discarded_jobs += 1
                        logger.warning(
                            "Discarded invalid Incruit job during parsing.",
                            extra={
                                "source": self.source_name,
                                "keyword": keyword,
                                "page": page,
                                "detail_url": preview.detail_url,
                                "discard_reason": str(exc),
                            },
                        )
                    except Exception as exc:  # pragma: no cover - defensive for live parsing drift
                        discarded_jobs += 1
                        logger.warning(
                            "Discarded Incruit job after parser error.",
                            extra={
                                "source": self.source_name,
                                "keyword": keyword,
                                "page": page,
                                "detail_url": preview.detail_url,
                                "error_type": exc.__class__.__name__,
                            },
                        )

        logger.info(
            "Completed Incruit scrape batch.",
            extra={
                "source": self.source_name,
                "searched_keyword": ",".join(searched_keywords),
                "fetched_listing_count": fetched_listing_count,
                "parsed_job_count": len(jobs),
                "discarded_job_count": discarded_jobs,
                "page_count": page_count,
            },
        )
        return jobs

    def _derive_keywords(self, user_context: Dict[str, Any]) -> List[str]:
        profile_data = user_context.get("profile_data") or {}
        title_keywords = profile_data.get("title_keywords") or []
        normalized_keywords = [
            str(keyword).strip()
            for keyword in title_keywords
            if isinstance(keyword, str) and str(keyword).strip()
        ]
        if normalized_keywords:
            return normalized_keywords

        role = str(profile_data.get("role", "")).strip()
        if role:
            return [role]

        return ["machine learning engineer"]

    async def _fetch_search_html(self, *, keyword: str, page: int) -> str:
        url = build_search_url(base_url=self.base_url, keyword=keyword, page=page)
        return await self._fetch_page_html(url)

    async def _fetch_detail_html(self, detail_url: str) -> str:
        return await self._fetch_page_html(detail_url)

    async def _fetch_page_html(self, url: str) -> str:
        try:
            from playwright.async_api import async_playwright
        except ImportError as exc:  # pragma: no cover - depends on local env setup
            raise RuntimeError(
                "Playwright is required for Incruit scraping. Run `poetry install` and "
                "`poetry run playwright install chromium`."
            ) from exc

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=self.headless)
            try:
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=self.timeout_ms)
                return await page.content()
            finally:
                await browser.close()
