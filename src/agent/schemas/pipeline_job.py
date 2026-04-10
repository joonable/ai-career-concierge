from __future__ import annotations

from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from db.models import Job


class PipelineJob(BaseModel):
    job_id: UUID
    platform: str
    external_job_id: str
    title: str
    company: str
    jd_raw_text: str
    url: str
    min_years_experience: Optional[int] = None
    max_years_experience: Optional[int] = None
    source_metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_job_model(cls, job: Job) -> PipelineJob:
        return cls(
            job_id=job.id,
            platform=job.platform,
            external_job_id=job.external_job_id,
            title=job.title,
            company=job.company,
            jd_raw_text=job.jd_raw_text,
            url=job.url,
            min_years_experience=job.min_years_experience,
            max_years_experience=job.max_years_experience,
            source_metadata=job.source_metadata,
        )
