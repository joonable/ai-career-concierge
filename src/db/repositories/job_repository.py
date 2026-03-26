from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Session, select

from db.models import Job
from scraper.base import ScrapedJob


class JobRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_platform_and_external_id(self, platform: str, external_job_id: str) -> Optional[Job]:
        statement = select(Job).where(
            Job.platform == platform,
            Job.external_job_id == external_job_id,
        )
        return self.session.exec(statement).first()

    def upsert_job(self, scraped_job: ScrapedJob) -> Job:
        job = self.get_by_platform_and_external_id(
            platform=scraped_job.platform,
            external_job_id=scraped_job.external_job_id,
        )
        if job is None:
            job = Job(
                platform=scraped_job.platform,
                external_job_id=scraped_job.external_job_id,
                title=scraped_job.title,
                company=scraped_job.company,
                jd_raw_text=scraped_job.jd_raw_text,
                url=scraped_job.url,
                min_years_experience=scraped_job.min_years_experience,
                max_years_experience=scraped_job.max_years_experience,
                source_metadata=scraped_job.source_metadata,
            )
        else:
            job.title = scraped_job.title
            job.company = scraped_job.company
            job.jd_raw_text = scraped_job.jd_raw_text
            job.url = scraped_job.url
            job.min_years_experience = scraped_job.min_years_experience
            job.max_years_experience = scraped_job.max_years_experience
            job.source_metadata = scraped_job.source_metadata
            job.updated_at = datetime.now(timezone.utc)

        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
        return job
