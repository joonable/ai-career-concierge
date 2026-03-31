from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agent.schemas.pipeline_job import PipelineJob


class NormalizedHardPreferences(BaseModel):
    """Non-negotiable preference signals."""

    must_haves: list[str] = Field(default_factory=list)
    deal_breakers: list[str] = Field(default_factory=list)


class NormalizedSoftPreferences(BaseModel):
    """Preference signals that help prioritization but are not hard constraints."""

    title_keywords: list[str] = Field(default_factory=list)
    minimum_fit_score: int | None = None
    recent_dislike_signals: list[str] = Field(default_factory=list)


class NormalizedJobEvidence(BaseModel):
    """Job-side evidence normalized from raw job and source metadata."""

    title: str = ""
    company: str = ""
    description: str = ""
    responsibilities: list[str] = Field(default_factory=list)
    requirements: list[str] = Field(default_factory=list)
    preferred_requirements: list[str] = Field(default_factory=list)
    location: str = ""
    employment_type: str = ""
    min_years_experience: int | None = None
    max_years_experience: int | None = None


class NormalizedMissingness(BaseModel):
    """Signals for information that is absent or weak in raw inputs."""

    missing_profile_fields: list[str] = Field(default_factory=list)
    missing_preference_fields: list[str] = Field(default_factory=list)
    missing_job_fields: list[str] = Field(default_factory=list)
    missing_memory: bool = False


class NormalizedEvaluationContext(BaseModel):
    """Stable prompt-ready context for job evaluation.

    Raw input sources:
    - onboarding/profile: role, years_of_experience, title_keywords
    - guidelines: must_haves, deal_breakers
    - notification settings: minimum_fit_score
    - recent memory: dislike summary string
    - job: title, company, jd_raw_text, min/max experience, source_metadata

    Normalized prompt groups:
    - hard_preferences
    - soft_preferences
    - job_evidence
    - missingness
    """

    target_role: str = "unknown"
    years_of_experience: int | None = None
    hard_preferences: NormalizedHardPreferences = Field(default_factory=NormalizedHardPreferences)
    soft_preferences: NormalizedSoftPreferences = Field(default_factory=NormalizedSoftPreferences)
    job_evidence: NormalizedJobEvidence = Field(default_factory=NormalizedJobEvidence)
    missingness: NormalizedMissingness = Field(default_factory=NormalizedMissingness)

    def to_prompt_variables(self) -> dict[str, Any]:
        return {
            "role": self.target_role,
            "years_of_experience": (
                str(self.years_of_experience) if self.years_of_experience is not None else "unknown"
            ),
            "must_haves": _join_items(self.hard_preferences.must_haves, fallback="None provided"),
            "deal_breakers": _join_items(self.hard_preferences.deal_breakers, fallback="None provided"),
            "title_keywords": _join_items(self.soft_preferences.title_keywords, fallback="None provided"),
            "minimum_fit_score": (
                str(self.soft_preferences.minimum_fit_score)
                if self.soft_preferences.minimum_fit_score is not None
                else "unknown"
            ),
            "recent_memory": _join_items(
                self.soft_preferences.recent_dislike_signals,
                fallback="No recent dislike memory.",
            ),
            "job_title": self.job_evidence.title or "unknown",
            "company": self.job_evidence.company or "unknown",
            "job_description": self.job_evidence.description or "No structured job description provided.",
            "responsibilities": _join_items(
                self.job_evidence.responsibilities,
                fallback="Not explicitly provided",
            ),
            "requirements": _join_items(
                self.job_evidence.requirements,
                fallback="Not explicitly provided",
            ),
            "preferred_requirements": _join_items(
                self.job_evidence.preferred_requirements,
                fallback="Not explicitly provided",
            ),
            "location": self.job_evidence.location or "unknown",
            "employment_type": self.job_evidence.employment_type or "unknown",
            "missing_context": self.describe_missingness(),
        }

    def describe_missingness(self) -> str:
        messages: list[str] = []
        if self.missingness.missing_profile_fields:
            messages.append(
                f"profile: {', '.join(self.missingness.missing_profile_fields)}"
            )
        if self.missingness.missing_preference_fields:
            messages.append(
                f"preferences: {', '.join(self.missingness.missing_preference_fields)}"
            )
        if self.missingness.missing_job_fields:
            messages.append(f"job: {', '.join(self.missingness.missing_job_fields)}")
        if self.missingness.missing_memory:
            messages.append("memory: none")
        return "; ".join(messages) if messages else "No major missing context."


def build_normalized_evaluation_context(
    *,
    user_context: dict[str, Any],
    recent_memory: str,
    job: PipelineJob,
) -> NormalizedEvaluationContext:
    profile_data = user_context.get("profile_data", {}) if isinstance(user_context, dict) else {}
    guidelines = user_context.get("guidelines", {}) if isinstance(user_context, dict) else {}
    notification_settings = (
        user_context.get("notification_settings", {}) if isinstance(user_context, dict) else {}
    )
    source_metadata = job.source_metadata if isinstance(job.source_metadata, dict) else {}

    role = _clean_string(profile_data.get("role")) or "unknown"
    years = _coerce_int(profile_data.get("years_of_experience"))
    title_keywords = _normalize_string_list(profile_data.get("title_keywords"))
    must_haves = _normalize_string_list(guidelines.get("must_haves"))
    deal_breakers = _normalize_string_list(guidelines.get("deal_breakers"))
    minimum_fit_score = _coerce_int(notification_settings.get("minimum_fit_score"))
    recent_dislike_signals = _normalize_memory(recent_memory)

    missing_profile_fields: list[str] = []
    missing_preference_fields: list[str] = []
    missing_job_fields: list[str] = []

    if role == "unknown":
        missing_profile_fields.append("role")
    if years is None:
        missing_profile_fields.append("years_of_experience")
    if not title_keywords:
        missing_preference_fields.append("title_keywords")
    if not must_haves:
        missing_preference_fields.append("must_haves")
    if not deal_breakers:
        missing_preference_fields.append("deal_breakers")
    if minimum_fit_score is None:
        missing_preference_fields.append("minimum_fit_score")

    if not _clean_string(job.title):
        missing_job_fields.append("title")
    if not _clean_string(job.company):
        missing_job_fields.append("company")
    if not _clean_string(job.jd_raw_text):
        missing_job_fields.append("jd_raw_text")
    if not _normalize_string_list(source_metadata.get("responsibilities")):
        missing_job_fields.append("responsibilities")
    if not _normalize_string_list(source_metadata.get("requirements")):
        missing_job_fields.append("requirements")

    return NormalizedEvaluationContext(
        target_role=role,
        years_of_experience=years,
        hard_preferences=NormalizedHardPreferences(
            must_haves=must_haves,
            deal_breakers=deal_breakers,
        ),
        soft_preferences=NormalizedSoftPreferences(
            title_keywords=title_keywords,
            minimum_fit_score=minimum_fit_score,
            recent_dislike_signals=recent_dislike_signals,
        ),
        job_evidence=NormalizedJobEvidence(
            title=_clean_string(job.title),
            company=_clean_string(job.company),
            description=_clean_string(job.jd_raw_text),
            responsibilities=_normalize_string_list(source_metadata.get("responsibilities")),
            requirements=_normalize_string_list(source_metadata.get("requirements")),
            preferred_requirements=_normalize_string_list(
                source_metadata.get("preferred_requirements")
            ),
            location=_first_non_empty(
                source_metadata,
                ["location", "region", "workplace"],
            ),
            employment_type=_first_non_empty(
                source_metadata,
                ["employment_type", "employmentType", "job_type"],
            ),
            min_years_experience=job.min_years_experience,
            max_years_experience=job.max_years_experience,
        ),
        missingness=NormalizedMissingness(
            missing_profile_fields=missing_profile_fields,
            missing_preference_fields=missing_preference_fields,
            missing_job_fields=missing_job_fields,
            missing_memory=not bool(recent_dislike_signals),
        ),
    )


def _normalize_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, str):
            continue
        cleaned = item.strip()
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        normalized.append(cleaned)
    return normalized


def _normalize_memory(value: str) -> list[str]:
    if not isinstance(value, str):
        return []
    cleaned = value.replace("\n", ";").split(";")
    return _normalize_string_list(cleaned)


def _clean_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _coerce_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _join_items(items: list[str], *, fallback: str) -> str:
    return ", ".join(items) if items else fallback


def _first_non_empty(payload: dict[str, Any], keys: list[str]) -> str:
    for key in keys:
        value = _clean_string(payload.get(key))
        if value:
            return value
    return ""
