from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text, UniqueConstraint
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Job(SQLModel, table=True):
    """
    수집된 단일 '채용 공고' 데이터베이스 모델입니다.
    공고 원본 데이터 자체를 보관하며, 사용자별 맞춤 평가는 `Evaluation` 테이블에서 별도로 관리됩니다.
    `platform`과 `external_job_id`의 조합에 유니크(Unique) 제약을 두어 중복 스크래핑 시 중복 삽입을 방지합니다.
    """
    __tablename__ = "jobs"
    __table_args__ = (UniqueConstraint("platform", "external_job_id", name="uq_jobs_platform_external"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    platform: str = Field(sa_column=Column(String(100), nullable=False, index=True))
    external_job_id: str = Field(sa_column=Column(String(255), nullable=False, index=True))
    title: str = Field(sa_column=Column(String(255), nullable=False))
    company: str = Field(sa_column=Column(String(255), nullable=False))
    jd_raw_text: str = Field(sa_column=Column(Text, nullable=False))
    url: str = Field(sa_column=Column(Text, nullable=False))
    min_years_experience: Optional[int] = Field(default=None, sa_column=Column(Integer, nullable=True))
    max_years_experience: Optional[int] = Field(default=None, sa_column=Column(Integer, nullable=True))
    source_metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
