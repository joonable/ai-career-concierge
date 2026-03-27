from __future__ import annotations

from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from db.enums import EvaluationStatus, FeedbackState


class ProfileData(BaseModel):
    role: str = Field(min_length=1, max_length=120)
    years_of_experience: int = Field(ge=0, le=50)
    title_keywords: List[str] = Field(default_factory=list)

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Role must not be empty.")
        return normalized

    @field_validator("title_keywords", mode="before")
    @classmethod
    def normalize_title_keywords(cls, value: Any) -> List[str]:
        return _normalize_string_list(value)


class Guidelines(BaseModel):
    must_haves: List[str] = Field(default_factory=list)
    deal_breakers: List[str] = Field(default_factory=list)

    @field_validator("must_haves", "deal_breakers", mode="before")
    @classmethod
    def normalize_guideline_items(cls, value: Any) -> List[str]:
        return _normalize_string_list(value)


class NotificationSettings(BaseModel):
    minimum_fit_score: int = Field(default=80, ge=1, le=100)
    delivery_channel: Optional[str] = Field(default=None, max_length=40)

    @field_validator("delivery_channel")
    @classmethod
    def normalize_delivery_channel(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class UserProfilePayload(BaseModel):
    profile_data: ProfileData
    guidelines: Guidelines
    notification_settings: NotificationSettings

    @model_validator(mode="after")
    def ensure_keywords_include_role(self) -> "UserProfilePayload":
        if not self.profile_data.title_keywords and self.profile_data.role.strip():
            role_keyword = self.profile_data.role.lower()
            self.profile_data.title_keywords = [role_keyword]
        return self


class UserProfileResponse(UserProfilePayload):
    user_id: UUID
    email: str


class DashboardRecommendation(BaseModel):
    evaluation_id: UUID
    status: EvaluationStatus
    fit_score: Optional[int] = None
    reasoning: Optional[str] = None
    user_feedback: Optional[FeedbackState] = None
    feedback_reason: Optional[str] = None
    job_id: UUID
    title: str
    company: str
    url: str
    platform: str


class DashboardResponse(BaseModel):
    user_id: UUID
    minimum_fit_score: int
    recommendations: List[DashboardRecommendation] = Field(default_factory=list)


def _normalize_string_list(value: Any) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("Value must be a list of strings.")

    normalized_items: List[str] = []
    seen = set()
    for item in value:
        if not isinstance(item, str):
            raise ValueError("List items must be strings.")
        normalized = item.strip()
        if not normalized:
            continue
        lowered = normalized.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        normalized_items.append(normalized)
    return normalized_items
