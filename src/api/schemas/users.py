from __future__ import annotations

from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from db.enums import EvaluationStatus, FeedbackState

DEFAULT_MINIMUM_FIT_SCORE = 80
DEFAULT_DELIVERY_CHANNEL = "slack"


class ProfileData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str = Field(default="", max_length=120)
    years_of_experience: int = Field(default=0, ge=0, le=50)
    title_keywords: List[str] = Field(default_factory=list)

    @field_validator("role")
    @classmethod
    def validate_role(cls, value: str) -> str:
        return value.strip()

    @field_validator("title_keywords", mode="before")
    @classmethod
    def normalize_title_keywords(cls, value: Any) -> List[str]:
        return _normalize_string_list(value)

    @model_validator(mode="after")
    def ensure_keywords_include_role(self) -> "ProfileData":
        if not self.title_keywords and self.role:
            self.title_keywords = [self.role.lower()]
        return self


class Guidelines(BaseModel):
    model_config = ConfigDict(extra="forbid")

    must_haves: List[str] = Field(default_factory=list)
    deal_breakers: List[str] = Field(default_factory=list)

    @field_validator("must_haves", "deal_breakers", mode="before")
    @classmethod
    def normalize_guideline_items(cls, value: Any) -> List[str]:
        return _normalize_string_list(value)


class NotificationSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    minimum_fit_score: int = Field(default=DEFAULT_MINIMUM_FIT_SCORE, ge=1, le=100)
    delivery_channel: str = Field(default=DEFAULT_DELIVERY_CHANNEL, max_length=40)

    @field_validator("delivery_channel", mode="before")
    @classmethod
    def normalize_delivery_channel(cls, value: Any) -> str:
        if value is None:
            return DEFAULT_DELIVERY_CHANNEL
        if not isinstance(value, str):
            raise ValueError("Delivery channel must be a string.")

        normalized = value.strip().lower()
        if not normalized:
            return DEFAULT_DELIVERY_CHANNEL
        if normalized != DEFAULT_DELIVERY_CHANNEL:
            raise ValueError("Only slack delivery is supported.")
        return normalized


class UserProfileBody(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile_data: ProfileData = Field(default_factory=ProfileData)
    guidelines: Guidelines = Field(default_factory=Guidelines)
    notification_settings: NotificationSettings = Field(default_factory=NotificationSettings)


class UserProfilePayload(UserProfileBody):
    @model_validator(mode="after")
    def validate_required_onboarding_fields(self) -> "UserProfilePayload":
        if not self.profile_data.role:
            raise ValueError("Role must not be empty.")
        return self


class UserProfileResponse(UserProfileBody):
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


def build_user_profile_response(
    *,
    user_id: UUID,
    email: str,
    profile_data: Any,
    guidelines: Any,
    notification_settings: Any,
) -> UserProfileResponse:
    return UserProfileResponse(
        user_id=user_id,
        email=email,
        profile_data=_build_profile_data(profile_data),
        guidelines=_build_guidelines(guidelines),
        notification_settings=_build_notification_settings(notification_settings),
    )


def serialize_user_profile_sections(profile: UserProfileBody) -> dict[str, dict[str, Any]]:
    return {
        "profile_data": profile.profile_data.model_dump(),
        "guidelines": profile.guidelines.model_dump(),
        "notification_settings": profile.notification_settings.model_dump(),
    }


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


def _build_profile_data(value: Any) -> ProfileData:
    payload = value if isinstance(value, dict) else {}
    title_keywords = payload.get("title_keywords", [])
    if not isinstance(title_keywords, list):
        title_keywords = []

    return ProfileData(
        role=_coerce_string(payload.get("role")),
        years_of_experience=_coerce_bounded_int(
            payload.get("years_of_experience"),
            default=0,
            minimum=0,
            maximum=50,
        ),
        title_keywords=title_keywords,
    )


def _build_guidelines(value: Any) -> Guidelines:
    payload = value if isinstance(value, dict) else {}
    must_haves = payload.get("must_haves", [])
    if not isinstance(must_haves, list):
        must_haves = []

    deal_breakers = payload.get("deal_breakers", [])
    if not isinstance(deal_breakers, list):
        deal_breakers = []

    return Guidelines(
        must_haves=must_haves,
        deal_breakers=deal_breakers,
    )


def _build_notification_settings(value: Any) -> NotificationSettings:
    payload = value if isinstance(value, dict) else {}
    return NotificationSettings(
        minimum_fit_score=_coerce_bounded_int(
            payload.get("minimum_fit_score"),
            default=DEFAULT_MINIMUM_FIT_SCORE,
            minimum=1,
            maximum=100,
        ),
        delivery_channel=payload.get("delivery_channel"),
    )


def _coerce_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _coerce_bounded_int(
    value: Any,
    *,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    if isinstance(value, bool):
        return default

    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default

    if parsed < minimum or parsed > maximum:
        return default
    return parsed
