from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from db.enums import EvaluationStatus, FeedbackState

DEFAULT_MINIMUM_FIT_SCORE = 80
DEFAULT_DELIVERY_CHANNEL = "slack"


class ProfileData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str = Field(default="", max_length=120)
    roles: List[str] = Field(default_factory=list)
    primary_role: str = Field(default="", max_length=120)
    years_of_experience: int = Field(default=0, ge=0, le=50)
    seniority: str = Field(default="", max_length=40)
    title_keywords: List[str] = Field(default_factory=list)

    @field_validator("role", "primary_role", "seniority")
    @classmethod
    def validate_role(cls, value: str) -> str:
        return value.strip()

    @field_validator("roles", mode="before")
    @classmethod
    def normalize_roles(cls, value: Any) -> List[str]:
        return _normalize_string_list(value)

    @field_validator("title_keywords", mode="before")
    @classmethod
    def normalize_title_keywords(cls, value: Any) -> List[str]:
        return _normalize_string_list(value)

    @model_validator(mode="after")
    def ensure_profile_identity_fields(self) -> "ProfileData":
        if not self.roles and self.primary_role:
            self.roles = [self.primary_role]
        if self.roles and not self.primary_role:
            self.primary_role = self.roles[0]
        if not self.role and self.primary_role:
            self.role = self.primary_role
        if not self.title_keywords and self.role:
            self.title_keywords = [self.role.lower()]
        return self


class Guidelines(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Deprecated compatibility field. `preferences` is the source of truth for
    # onboarding storage, while `guidelines` remains as a legacy surface for
    # older evaluators, fixtures, and API consumers during migration.
    must_haves: List[str] = Field(default_factory=list)
    deal_breakers: List[str] = Field(default_factory=list)

    @field_validator("must_haves", "deal_breakers", mode="before")
    @classmethod
    def normalize_guideline_items(cls, value: Any) -> List[str]:
        return _normalize_string_list(value)


class PreferenceKeywordBucket(BaseModel):
    model_config = ConfigDict(extra="forbid")

    preset: List[str] = Field(default_factory=list)
    custom: List[str] = Field(default_factory=list)

    @field_validator("preset", "custom", mode="before")
    @classmethod
    def normalize_keyword_bucket_items(cls, value: Any) -> List[str]:
        return _normalize_string_list(value)


class Preferences(BaseModel):
    model_config = ConfigDict(extra="forbid")

    work_modes: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    team_contexts: List[str] = Field(default_factory=list)
    skills: PreferenceKeywordBucket = Field(default_factory=PreferenceKeywordBucket)
    exclusions: PreferenceKeywordBucket = Field(default_factory=PreferenceKeywordBucket)
    comparisons: Dict[str, int] = Field(default_factory=dict)
    note: Optional[str] = None

    @field_validator("work_modes", "locations", "team_contexts", mode="before")
    @classmethod
    def normalize_preference_lists(cls, value: Any) -> List[str]:
        return _normalize_string_list(value)

    @field_validator("comparisons", mode="before")
    @classmethod
    def normalize_comparisons(cls, value: Any) -> Dict[str, int]:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise ValueError("Comparisons must be an object.")

        normalized: Dict[str, int] = {}
        for key, raw in value.items():
            if not isinstance(key, str):
                raise ValueError("Comparison keys must be strings.")
            key_name = key.strip()
            if not key_name:
                continue
            try:
                parsed = int(raw)
            except (TypeError, ValueError) as exc:
                raise ValueError("Comparison values must be integers.") from exc
            if parsed < -2 or parsed > 2:
                raise ValueError("Comparison values must be between -2 and 2.")
            normalized[key_name] = parsed
        return normalized

    @field_validator("note", mode="before")
    @classmethod
    def normalize_note(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("Note must be a string.")
        normalized = value.strip()
        return normalized or None

    def has_content(self) -> bool:
        return any(
            [
                self.work_modes,
                self.locations,
                self.team_contexts,
                self.skills.preset,
                self.skills.custom,
                self.exclusions.preset,
                self.exclusions.custom,
                self.comparisons,
                self.note,
            ]
        )


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
    # Deprecated compatibility field. New writes should prefer `preferences`,
    # and this field is derived from `preferences` when structured data exists.
    guidelines: Guidelines = Field(default_factory=Guidelines)
    preferences: Preferences = Field(default_factory=Preferences)
    notification_settings: NotificationSettings = Field(default_factory=NotificationSettings)

    @model_validator(mode="after")
    def apply_structured_compatibility_defaults(self) -> "UserProfileBody":
        if self.preferences.has_content():
            self.guidelines = _build_legacy_guidelines_from_preferences(self.preferences)
        return self


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
    decision_summary: Optional[str] = None
    match_highlights: List[str] = Field(default_factory=list)
    risk_highlights: List[str] = Field(default_factory=list)
    confidence_level: str = "LOW"
    rule_rejection_reason: Optional[str] = None
    rule_match_reasons: List[str] = Field(default_factory=list)
    rule_rejection_details: List[str] = Field(default_factory=list)
    user_feedback: Optional[FeedbackState] = None
    feedback_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    job_id: UUID
    title: str
    company: str
    url: str
    platform: str
    jd_raw_text: str
    min_years_experience: Optional[int] = None
    max_years_experience: Optional[int] = None
    source_metadata: dict[str, Any] = Field(default_factory=dict)
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    preferred_requirements: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    employment_type: Optional[str] = None


class DashboardResponse(BaseModel):
    user_id: UUID
    minimum_fit_score: int
    recommendations: List[DashboardRecommendation] = Field(default_factory=list)


class PromptOpsBacklogItem(BaseModel):
    title: str
    url: str


class PromptOpsStatusResponse(BaseModel):
    prompt_family: str
    production_identifier: str
    staging_identifier: str
    candidate_identifier: str
    latest_decision: str
    compare_url: str
    review_queue_name: str
    review_queue_url: str
    notion_backlog_url: str
    latest_iteration_title: str
    latest_iteration_url: str
    latest_summary: List[str] = Field(default_factory=list)
    next_backlog_items: List[PromptOpsBacklogItem] = Field(default_factory=list)


def build_user_profile_response(
    *,
    user_id: UUID,
    email: str,
    profile_data: Any,
    guidelines: Any,
    preferences: Any,
    notification_settings: Any,
) -> UserProfileResponse:
    return UserProfileResponse(
        user_id=user_id,
        email=email,
        profile_data=_build_profile_data(profile_data),
        guidelines=_build_guidelines(guidelines, preferences=preferences),
        preferences=_build_preferences(preferences),
        notification_settings=_build_notification_settings(notification_settings),
    )


def serialize_user_profile_sections(profile: UserProfileBody) -> dict[str, dict[str, Any]]:
    return {
        "profile_data": profile.profile_data.model_dump(),
        "guidelines": profile.guidelines.model_dump(),
        "preferences": profile.preferences.model_dump(),
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
        roles=payload.get("roles", []),
        primary_role=_coerce_string(payload.get("primary_role")),
        years_of_experience=_coerce_bounded_int(
            payload.get("years_of_experience"),
            default=0,
            minimum=0,
            maximum=50,
        ),
        seniority=_coerce_string(payload.get("seniority")),
        title_keywords=title_keywords,
    )


def _build_guidelines(value: Any, *, preferences: Any) -> Guidelines:
    payload = value if isinstance(value, dict) else {}
    must_haves = payload.get("must_haves", [])
    if not isinstance(must_haves, list):
        must_haves = []

    deal_breakers = payload.get("deal_breakers", [])
    if not isinstance(deal_breakers, list):
        deal_breakers = []

    explicit = Guidelines(
        must_haves=must_haves,
        deal_breakers=deal_breakers,
    )
    structured_preferences = _build_preferences(preferences)
    if structured_preferences.has_content():
        return _build_legacy_guidelines_from_preferences(structured_preferences)
    return explicit


def _build_preferences(value: Any) -> Preferences:
    payload = value if isinstance(value, dict) else {}
    return Preferences(
        work_modes=payload.get("work_modes", []),
        locations=payload.get("locations", []),
        team_contexts=payload.get("team_contexts", []),
        skills=payload.get("skills", {}),
        exclusions=payload.get("exclusions", {}),
        comparisons=payload.get("comparisons", {}),
        note=payload.get("note"),
    )


def _build_legacy_guidelines_from_preferences(preferences: Preferences) -> Guidelines:
    return Guidelines(
        must_haves=[
            *preferences.skills.preset,
            *preferences.skills.custom,
        ],
        deal_breakers=[
            *preferences.exclusions.preset,
            *preferences.exclusions.custom,
        ],
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
