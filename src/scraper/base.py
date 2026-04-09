from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol

from pydantic import BaseModel, Field


class ScrapedJob(BaseModel):
    """
    각 채용 플랫폼(예: 인크루트, 점핏 등)에서 스크래퍼가 가져온 원시 채용 공고 데이터를 표현하는 스키마입니다.
    """

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
    """
    시스템에 등록되는 모든 채용 플랫폼 스크래퍼들이 반드시 구현해야 하는 공통 인터페이스입니다.
    `fetch_jobs` 메서드를 통해 해당 플랫폼의 공고를 비동기적으로 수집합니다.
    """

    source_name: str

    async def fetch_jobs(self, user_context: Dict[str, Any]) -> List[ScrapedJob]: ...
