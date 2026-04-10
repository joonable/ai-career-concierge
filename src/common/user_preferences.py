from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

WORK_MODE_LABELS = {
    "remote": "원격",
    "hybrid": "하이브리드",
    "onsite": "상주 출근",
}

LOCATION_LABELS = {
    "seoul": "서울",
    "pangyo": "판교",
    "bundang": "분당",
    "gyeonggi": "경기권",
    "daejeon": "대전",
    "busan": "부산",
    "nationwide": "전국 어디든",
    "global": "해외 포함",
}

TEAM_CONTEXT_LABELS = {
    "ai-first": "AI/ML 팀이 핵심 조직",
    "product-team": "프로덕트와 가까운 역할",
    "platform-team": "플랫폼/인프라와 맞닿은 역할",
    "small-team": "작은 팀에서 폭넓게 담당",
    "specialist-team": "전문성 높은 팀 분업",
}

SKILL_LABELS = {
    "python": "Python",
    "sql": "SQL",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "llm": "LLM application",
    "rag": "RAG",
    "evaluation": "LLM evaluation",
    "airflow": "Airflow / orchestration",
    "mlops": "MLOps / serving",
    "aws": "AWS / cloud",
    "backend": "Backend API",
    "analytics": "Experimentation / analytics",
}

EXCLUSION_LABELS = {
    "contract": "계약직 중심",
    "internship": "인턴 포지션",
    "onsite-only": "상주 출근만 가능",
    "research-heavy": "리서치 성향이 너무 강함",
    "no-llm": "LLM 업무가 전혀 없음",
    "korean-required": "한국어 필수",
    "visa-none": "비자 지원 없음",
}

COMPARISON_LABELS = {
    "delivery-vs-research": ("모델 개발 중심", "서비스 적용 중심"),
    "company-shape": ("작은 팀 자율성", "큰 조직 안정성"),
    "llm-vs-classic": ("LLM 응용 중심", "전통 ML 중심"),
    "ownership-shape": ("한 문제를 깊게 파는 역할", "여러 영역을 넓게 맡는 역할"),
    "speed-vs-process": ("빠른 실행과 실험", "정교한 프로세스와 안정성"),
    "build-vs-operate": ("새 시스템 구축 비중", "운영 최적화 비중"),
}

COMPARISON_TONE_LABELS = {
    -2: "강하게 왼쪽",
    -1: "약하게 왼쪽",
    0: "중립",
    1: "약하게 오른쪽",
    2: "강하게 오른쪽",
}


class NormalizedStoredPreferences(BaseModel):
    target_role: str = ""
    role_targets: list[str] = Field(default_factory=list)
    years_of_experience: int | None = None
    title_keywords: list[str] = Field(default_factory=list)
    work_modes: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    team_contexts: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    excluded_signals: list[str] = Field(default_factory=list)
    comparison_tones: list[str] = Field(default_factory=list)
    note: str = ""
    minimum_fit_score: int | None = None


def build_normalized_stored_preferences(user_context: dict[str, Any] | Any) -> NormalizedStoredPreferences:
    payload = user_context if isinstance(user_context, dict) else {}
    profile_data = payload.get("profile_data", {}) if isinstance(payload.get("profile_data"), dict) else {}
    preferences = payload.get("preferences", {}) if isinstance(payload.get("preferences"), dict) else {}
    guidelines = payload.get("guidelines", {}) if isinstance(payload.get("guidelines"), dict) else {}
    notification_settings = (
        payload.get("notification_settings", {}) if isinstance(payload.get("notification_settings"), dict) else {}
    )

    roles = _normalize_string_list(profile_data.get("roles"))
    primary_role = _clean_string(profile_data.get("primary_role"))
    role = _clean_string(profile_data.get("role"))
    if primary_role and primary_role not in roles:
        roles.insert(0, primary_role)
    if role and role not in roles:
        roles.insert(0, role)

    target_role = role or primary_role or (roles[0] if roles else "")

    work_modes = _expand_ids(_normalize_string_list(preferences.get("work_modes")), WORK_MODE_LABELS)
    locations = _expand_ids(_normalize_string_list(preferences.get("locations")), LOCATION_LABELS)
    team_contexts = _expand_ids(
        _normalize_string_list(preferences.get("team_contexts")),
        TEAM_CONTEXT_LABELS,
    )

    skills = preferences.get("skills", {}) if isinstance(preferences.get("skills"), dict) else {}
    exclusions = preferences.get("exclusions", {}) if isinstance(preferences.get("exclusions"), dict) else {}
    structured_skills = [
        *_expand_ids(_normalize_string_list(skills.get("preset")), SKILL_LABELS),
        *_normalize_string_list(skills.get("custom")),
    ]
    structured_exclusions = [
        *_expand_ids(_normalize_string_list(exclusions.get("preset")), EXCLUSION_LABELS),
        *_normalize_string_list(exclusions.get("custom")),
    ]

    preferred_skills = structured_skills or _normalize_string_list(guidelines.get("must_haves"))
    excluded_signals = structured_exclusions or _normalize_string_list(guidelines.get("deal_breakers"))

    return NormalizedStoredPreferences(
        target_role=target_role,
        role_targets=roles,
        years_of_experience=_coerce_int(profile_data.get("years_of_experience")),
        title_keywords=_normalize_string_list(profile_data.get("title_keywords")),
        work_modes=work_modes,
        locations=locations,
        team_contexts=team_contexts,
        preferred_skills=_unique(preferred_skills),
        excluded_signals=_unique(excluded_signals),
        comparison_tones=_build_comparison_tones(preferences.get("comparisons")),
        note=_clean_string(preferences.get("note")),
        minimum_fit_score=_coerce_int(notification_settings.get("minimum_fit_score")),
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


def _expand_ids(values: list[str], mapping: dict[str, str]) -> list[str]:
    expanded: list[str] = []
    for value in values:
        expanded.append(mapping.get(value, value))
    return expanded


def _build_comparison_tones(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return []
    tones: list[str] = []
    for key, raw in value.items():
        if not isinstance(key, str):
            continue
        try:
            parsed = int(raw)
        except (TypeError, ValueError):
            continue
        labels = COMPARISON_LABELS.get(key)
        if labels is None:
            continue
        tone = COMPARISON_TONE_LABELS.get(parsed)
        if tone is None:
            continue
        tones.append(f"{tone}: {labels[0]} / {labels[1]}")
    return _unique(tones)


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


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    normalized: list[str] = []
    for value in values:
        lowered = value.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        normalized.append(value)
    return normalized
