from __future__ import annotations

from typing import Any


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
