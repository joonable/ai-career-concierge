from __future__ import annotations

from typing import Any

from promptops.core.models import FailureRecord


FAILURE_TAXONOMY = {
    "prompt.role_alignment": "Prompt is not steering enough on direct vs adjacent role alignment.",
    "prompt.must_have_coverage": "Prompt is not consistently translating must-have gaps into score limits.",
    "prompt.transferable_skill_credit": "Prompt is over- or under-crediting adjacent transferable experience.",
    "prompt.summary_usefulness": "Prompt explanation quality is too weak for decision support.",
    "dataset.gold_expectation_gap": "Gold expectation is underspecified or does not reflect current product policy.",
    "dataset.borderline_coverage_gap": "Dataset lacks enough ambiguous adjacent-role examples.",
    "context.normalization_gap": "Normalized context is missing a signal needed for stable evaluation.",
    "policy.deal_breaker_handling": "Deal-breaker policy is not explicit enough or not applied consistently.",
    "policy.score_band_definition": "Score band policy is still ambiguous for borderline roles.",
    "feature.onboarding_signal_missing": "The product does not yet collect a signal needed by the evaluator.",
}


def is_borderline_case(*, fit_score: int | None, role_alignment: str | None) -> bool:
    """Return true for cases that deserve human review due to borderline scoring."""

    if fit_score is None:
        return True
    if 40 <= fit_score <= 79:
        return True
    return role_alignment == "MEDIUM"


def is_failure_case(*, evaluator_scores: dict[str, Any] | None = None) -> bool:
    """Return true when any tracked evaluator score indicates a miss."""

    if not evaluator_scores:
        return False
    for value in evaluator_scores.values():
        if isinstance(value, (int, float)) and value < 1:
            return True
    return False


def build_failure_record(
    *,
    taxonomy_key: str,
    category: str,
    summary: str,
    evidence: list[str] | None = None,
    source_review_item_id: str = "",
) -> FailureRecord:
    """Create a structured failure record from review or evaluator evidence."""

    return FailureRecord(
        taxonomy_key=taxonomy_key,
        category=category,
        summary=summary,
        evidence=evidence or [],
        source_review_item_id=source_review_item_id,
    )
