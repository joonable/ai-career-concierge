from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from api.schemas.users import UserProfileResponse
from common.user_preferences import build_normalized_stored_preferences


def build_dashboard_detail_fields(*, row, user: UserProfileResponse, minimum_fit_score: int) -> dict[str, Any]:
    normalized_text = _normalize_text(
        " ".join(
            [
                row.title,
                row.company,
                row.jd_raw_text,
                _flatten_metadata(row.source_metadata),
            ]
        )
    )
    preferences = build_normalized_stored_preferences(user.model_dump())
    role = preferences.target_role.strip()
    years = preferences.years_of_experience or 0
    title_keywords = [keyword.strip() for keyword in preferences.title_keywords if keyword.strip()]
    must_haves = [item.strip() for item in preferences.preferred_skills if item.strip()]
    deal_breakers = [item.strip() for item in preferences.excluded_signals if item.strip()]

    matched_must_haves = [item for item in must_haves if item.lower() in normalized_text]
    triggered_deal_breakers = [item for item in deal_breakers if item.lower() in normalized_text]

    title_match = _matches_title(role=role, title_keywords=title_keywords, title=row.title)
    experience_fit = _matches_experience(
        years=years,
        minimum=row.min_years_experience,
        maximum=row.max_years_experience,
    )

    decision_summary = _build_decision_summary(
        status=row.status,
        fit_score=row.fit_score,
        reasoning=row.reasoning,
        minimum_fit_score=minimum_fit_score,
        rule_rejection_reason=row.rule_rejection_reason,
    )

    rule_match_reasons = _build_rule_match_reasons(
        role=role,
        title_keywords=title_keywords,
        title_match=title_match,
        years=years,
        experience_fit=experience_fit,
        minimum_experience=row.min_years_experience,
        maximum_experience=row.max_years_experience,
    )

    rule_rejection_details = _build_rule_rejection_details(
        reason=row.rule_rejection_reason,
        role=role,
        years=years,
        minimum_experience=row.min_years_experience,
        maximum_experience=row.max_years_experience,
    )

    match_highlights = _unique_non_empty(
        [
            *(f"필수 조건 일치: {item}" for item in matched_must_haves[:3]),
            "직무 키워드가 공고 제목과 일치합니다." if title_match else None,
            (
                f"경력 {years}년이 권장 범위 {_format_experience_range(row.min_years_experience, row.max_years_experience)}에 들어옵니다."
                if experience_fit
                else None
            ),
            _read_metadata_label(row.source_metadata, ["location", "region", "workplace"], prefix="위치"),
            _read_metadata_label(
                row.source_metadata,
                ["employment_type", "employmentType", "job_type"],
                prefix="고용 형태",
            ),
        ]
    )

    risk_highlights = _unique_non_empty(
        [
            *(f"주의 조건 감지: {item}" for item in triggered_deal_breakers[:3]),
            (
                f"적합도 {row.fit_score}점으로 추천 기준 {minimum_fit_score}점보다 낮습니다."
                if row.fit_score is not None and row.fit_score < minimum_fit_score
                else None
            ),
            (
                f"공고의 권장 경력 {_format_experience_range(row.min_years_experience, row.max_years_experience)}와 현재 경력 {years}년 사이에 차이가 있습니다."
                if experience_fit is False
                else None
            ),
            (
                f"규칙 기반 제외 사유: {_format_rule_reason(row.rule_rejection_reason)}"
                if row.rule_rejection_reason
                else None
            ),
            (
                "JD에 구조화된 요구사항이 부족해 사람이 한 번 더 확인하는 편이 안전합니다."
                if not _extract_list_metadata(row.source_metadata, "requirements")
                and len(_split_sentences(row.jd_raw_text)) < 2
                else None
            ),
        ]
    )

    responsibilities = _extract_list_metadata(row.source_metadata, "responsibilities")
    if not responsibilities:
        responsibilities = _split_sentences(row.jd_raw_text)[:3]

    requirements = _extract_list_metadata(row.source_metadata, "requirements")
    if not requirements:
        requirements = _unique_non_empty(
            [
                *(f"{item} 경험" for item in matched_must_haves[:4]),
                (
                    f"권장 경력 {_format_experience_range(row.min_years_experience, row.max_years_experience)}"
                    if row.min_years_experience is not None or row.max_years_experience is not None
                    else None
                ),
            ]
        )

    preferred_requirements = _extract_list_metadata(row.source_metadata, "preferred_requirements")
    if not preferred_requirements and row.fit_score is not None and row.fit_score >= minimum_fit_score:
        preferred_requirements = _unique_non_empty([f"{item} 심화 경험" for item in matched_must_haves[1:3]])

    return {
        "decision_summary": decision_summary,
        "match_highlights": match_highlights,
        "risk_highlights": risk_highlights,
        "confidence_level": _build_confidence_level(row=row, match_highlights=match_highlights),
        "rule_match_reasons": rule_match_reasons,
        "rule_rejection_details": rule_rejection_details,
        "responsibilities": responsibilities,
        "requirements": requirements,
        "preferred_requirements": preferred_requirements,
        "location": _read_metadata_value(row.source_metadata, ["location", "region", "workplace"]),
        "employment_type": _read_metadata_value(
            row.source_metadata,
            ["employment_type", "employmentType", "job_type"],
        ),
    }


def _build_decision_summary(
    *,
    status: str,
    fit_score: int | None,
    reasoning: str | None,
    minimum_fit_score: int,
    rule_rejection_reason: str | None,
) -> str:
    if status == "RULE_REJECTED":
        return f"규칙 기반 필터에서 제외된 공고입니다. 핵심 사유는 {_format_rule_reason(rule_rejection_reason)}입니다."
    if status == "PENDING":
        return "규칙 필터는 통과했지만 아직 LLM 정밀 평가가 끝나지 않아 추가 확인이 필요합니다."
    if reasoning:
        return reasoning
    if fit_score is None:
        return "적합도 정보가 아직 없어 사람이 직접 JD를 확인해야 합니다."
    if fit_score >= minimum_fit_score:
        return f"적합도 {fit_score}점으로 현재 추천 기준 {minimum_fit_score}점을 충족한 공고입니다."
    return f"적합도 {fit_score}점으로 기준점에는 못 미치지만 보류 후보로 검토할 수 있습니다."


def _build_rule_match_reasons(
    *,
    role: str,
    title_keywords: list[str],
    title_match: bool,
    years: int,
    experience_fit: bool | None,
    minimum_experience: int | None,
    maximum_experience: int | None,
) -> list[str]:
    reasons: list[str] = []
    if title_match:
        if role:
            reasons.append(f"목표 직무 '{role}' 기준에서 공고 제목이 관련 키워드와 일치합니다.")
        elif title_keywords:
            reasons.append("설정된 직무 키워드와 공고 제목이 일치합니다.")
    if experience_fit is True:
        reasons.append(
            f"현재 경력 {years}년이 권장 범위 {_format_experience_range(minimum_experience, maximum_experience)} 안에 있습니다."
        )
    elif experience_fit is None:
        reasons.append("공고에 경력 범위가 명시되지 않아 경험 조건은 보수적으로 통과 처리했습니다.")
    return reasons


def _build_rule_rejection_details(
    *,
    reason: str | None,
    role: str,
    years: int,
    minimum_experience: int | None,
    maximum_experience: int | None,
) -> list[str]:
    if not reason:
        return []
    if reason == "TITLE_MISMATCH":
        return [
            f"공고 제목이 현재 목표 직무 '{role or '설정된 직무'}'와 충분히 겹치지 않았습니다.",
            "유사 직무일 수 있으므로 사람이 직접 확인할 가치는 남아 있습니다.",
        ]
    if reason == "EXPERIENCE_MISMATCH":
        return [
            f"현재 경력 {years}년과 공고의 권장 범위 {_format_experience_range(minimum_experience, maximum_experience)}가 어긋났습니다.",
            "연차 표기가 느슨한 공고일 수 있으니 실제 역할 범위는 원문에서 다시 확인하는 것이 좋습니다.",
        ]
    if reason == "LOCATION_MISMATCH":
        return [
            "공고에 표시된 지역이 현재 선호 지역과 충분히 겹치지 않았습니다.",
            "원격 여부나 팀 운영 방식에 따라 예외가 있을 수 있으니 원문 확인은 여전히 가치가 있습니다.",
        ]
    if reason == "WORK_MODE_MISMATCH":
        return [
            "공고의 근무 형태가 현재 선호 조건과 충분히 맞지 않았습니다.",
            "설명이 불명확한 공고는 실제 운영 방식이 다를 수 있으니 세부 문구를 다시 확인하는 것이 좋습니다.",
        ]
    return [f"규칙 기반 필터에서 {_format_rule_reason(reason)} 사유로 제외되었습니다."]


def _build_confidence_level(*, row, match_highlights: list[str]) -> str:
    if row.status == "RULE_REJECTED":
        return "HIGH"
    if row.status == "LLM_EVALUATED" and row.fit_score is not None and row.reasoning:
        return "HIGH" if len(match_highlights) >= 2 else "MEDIUM"
    if row.status == "PENDING":
        return "LOW"
    return "MEDIUM"


def _matches_title(*, role: str, title_keywords: list[str], title: str) -> bool:
    normalized_title = title.lower()
    if role and role.lower() in normalized_title:
        return True
    return any(keyword.lower() in normalized_title for keyword in title_keywords)


def _matches_experience(*, years: int, minimum: int | None, maximum: int | None) -> bool | None:
    if minimum is None and maximum is None:
        return None
    if minimum is not None and years < minimum:
        return False
    return not (maximum is not None and years > maximum)


def _format_rule_reason(value: str | None) -> str:
    if not value:
        return "상세 사유 없음"
    return value.replace("_", " ").lower().capitalize()


def _format_experience_range(minimum: int | None, maximum: int | None) -> str:
    if minimum is None and maximum is None:
        return "명시 없음"
    if minimum is not None and maximum is not None:
        return f"{minimum}년 ~ {maximum}년"
    if minimum is not None:
        return f"{minimum}년 이상"
    return f"{maximum}년 이하"


def _extract_list_metadata(source_metadata: dict[str, Any], key: str) -> list[str]:
    raw_value = source_metadata.get(key)
    if not isinstance(raw_value, list):
        return []
    return _unique_non_empty(str(item).strip() for item in raw_value)


def _split_sentences(value: str) -> list[str]:
    normalized = value.replace("\r", "\n")
    chunks = [chunk.strip(" -\t") for chunk in normalized.replace("\n", ". ").split(".")]
    return _unique_non_empty(chunk for chunk in chunks if len(chunk.strip()) >= 18)


def _flatten_metadata(source_metadata: dict[str, Any]) -> str:
    parts: list[str] = []
    for value in source_metadata.values():
        if isinstance(value, str):
            parts.append(value)
        elif isinstance(value, list):
            parts.extend(str(item) for item in value)
    return " ".join(parts)


def _read_metadata_value(source_metadata: dict[str, Any], keys: list[str]) -> str | None:
    for key in keys:
        value = source_metadata.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _read_metadata_label(source_metadata: dict[str, Any], keys: list[str], *, prefix: str) -> str | None:
    value = _read_metadata_value(source_metadata, keys)
    if not value:
        return None
    return f"{prefix}: {value}"


def _normalize_text(value: str) -> str:
    return " ".join(value.lower().split())


def _unique_non_empty(values: Iterable[str | None]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value is None:
            continue
        item = value.strip()
        if not item:
            continue
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        normalized.append(item)
    return normalized
