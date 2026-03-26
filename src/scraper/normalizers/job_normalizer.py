from __future__ import annotations

from scraper.base import ScrapedJob


def normalize_scraped_job(scraped_job: ScrapedJob) -> ScrapedJob:
    return ScrapedJob(
        platform=scraped_job.platform.strip(),
        external_job_id=scraped_job.external_job_id.strip(),
        title=" ".join(scraped_job.title.split()),
        company=" ".join(scraped_job.company.split()),
        jd_raw_text=" ".join(scraped_job.jd_raw_text.split()),
        url=scraped_job.url.strip(),
        min_years_experience=scraped_job.min_years_experience,
        max_years_experience=scraped_job.max_years_experience,
        source_metadata=scraped_job.source_metadata,
    )
