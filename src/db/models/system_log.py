from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import JSON, Column, DateTime, ForeignKey, String, Text
from sqlmodel import Field, SQLModel

from db.enums import LogLevel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SystemLog(SQLModel, table=True):
    __tablename__ = "system_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    run_id: str = Field(sa_column=Column(String(64), nullable=False, index=True))
    event_type: str = Field(sa_column=Column(String(100), nullable=False, index=True))
    level: LogLevel = Field(sa_column=Column(String(16), nullable=False, default=LogLevel.INFO.value))
    message: str = Field(sa_column=Column(Text, nullable=False))
    user_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
    )
    job_id: Optional[uuid.UUID] = Field(
        default=None,
        sa_column=Column(ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True),
    )
    platform: Optional[str] = Field(default=None, sa_column=Column(String(100), nullable=True))
    event_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSON, nullable=False),
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
