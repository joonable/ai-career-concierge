from __future__ import annotations

from urllib.parse import urljoin

from scraper.base import ScrapedJob


class InvalidScrapedJobError(ValueError):
    """Raised when a scraped job is missing required fields after normalization."""


def normalize_scraped_job(scraped_job: ScrapedJob) -> ScrapedJob:
    """
    스크래퍼가 막 가져온 거친(Raw) 형태의 공고 데이터를 시스템 저장에 적합하게 정제합니다.
    (연속된 띄어쓰기/줄바꿈 압축, 상대 URL을 절대 URL로 변환 등)
    또한 필수 필드(title, platform 등)가 누락되거나 JD 텍스트 길이가 극단적으로 짧은 경우 InvalidScrapedJobError를 발생시킵니다.
    """
    base_url = str(scraped_job.source_metadata.get("base_url", "")).strip()
    normalized_job = ScrapedJob(
        platform=scraped_job.platform.strip(),
        external_job_id=scraped_job.external_job_id.strip(),
        title=" ".join(scraped_job.title.split()),
        company=" ".join(scraped_job.company.split()),
        jd_raw_text=" ".join(scraped_job.jd_raw_text.split()),
        url=urljoin(base_url, scraped_job.url.strip()) if base_url else scraped_job.url.strip(),
        min_years_experience=scraped_job.min_years_experience,
        max_years_experience=scraped_job.max_years_experience,
        source_metadata=scraped_job.source_metadata,
    )

    if not normalized_job.platform:
        raise InvalidScrapedJobError("platform is required")
    if not normalized_job.external_job_id:
        raise InvalidScrapedJobError("external_job_id is required")
    if not normalized_job.title:
        raise InvalidScrapedJobError("title is required")
    if not normalized_job.company:
        raise InvalidScrapedJobError("company is required")
    if not normalized_job.url:
        raise InvalidScrapedJobError("url is required")
    if len(normalized_job.jd_raw_text) < 20:
        raise InvalidScrapedJobError("jd_raw_text is too short")

    return normalized_job
