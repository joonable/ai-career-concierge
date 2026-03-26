from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol

from pydantic import BaseModel, Field


class ScrapedJob(BaseModel):
    platform: str
    external_job_id: str
    title: str
    company: str
    jd_raw_text: str
    url: str
    min_years_experience: Optional[int] = Field(default=None)
    max_years_experience: Optional[int] = Field(default=None)
    source_metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseScraperSource(Protocol):
    source_name: str

    async def fetch_jobs(self, user_context: Dict[str, Any]) -> List[ScrapedJob]:
        ...
