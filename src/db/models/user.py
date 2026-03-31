from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import JSON, Column, DateTime, String
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    oauth_id: str = Field(sa_column=Column(String(255), unique=True, nullable=False, index=True))
    email: str = Field(sa_column=Column(String(320), unique=True, nullable=False, index=True))
    profile_data: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    guidelines: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    preferences: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON, nullable=False))
    notification_settings: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON, nullable=False),
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
