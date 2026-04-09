from __future__ import annotations

from typing import Any, Dict

from langsmith.evaluation.evaluator import EvaluationResult, EvaluationResults


def _normalized_output(outputs: Dict[str, Any], key: str) -> str:
    return str(outputs.get(key) or "").strip().upper()


def evaluate_job_match(run, example=None):
    outputs = (run.outputs or {}) if run else {}
    reference = (example.outputs or {}) if example else {}
    fit_score = int(outputs.get("fit_score") or 0)
    expected_should_pass = bool(reference.get("should_pass"))
    actual_should_pass = fit_score >= 80
    return EvaluationResult(
        key="classification_match",
        score=1 if actual_should_pass == expected_should_pass else 0,
        comment=f"expected_should_pass={expected_should_pass}, actual_should_pass={actual_should_pass}",
    )


def evaluate_fit_score_band(run, example=None):
    outputs = (run.outputs or {}) if run else {}
    reference = (example.outputs or {}) if example else {}
    fit_score = int(outputs.get("fit_score") or 0)
    score_range = reference.get("fit_score_range") or {}
    minimum = int(score_range.get("min", 1))
    maximum = int(score_range.get("max", 100))
    return EvaluationResult(
        key="fit_score_band",
        score=1 if minimum <= fit_score <= maximum else 0,
        comment=f"fit_score={fit_score}, expected_range=({minimum}, {maximum})",
    )


def evaluate_score_policy_alignment(run, example=None):
    outputs = (run.outputs or {}) if run else {}
    reference = (example.outputs or {}) if example else {}

    actual_role_alignment = _normalized_output(outputs, "role_alignment")
    expected_role_alignment = _normalized_output(reference, "expected_role_alignment")

    actual_must_have_coverage = _normalized_output(outputs, "must_have_coverage")
    expected_must_have_coverage = _normalized_output(reference, "expected_must_have_coverage")

    actual_deal_breaker_severity = _normalized_output(outputs, "deal_breaker_severity")
    expected_deal_breaker_severity = _normalized_output(reference, "expected_deal_breaker_severity")

    actual_transferable_skill_level = _normalized_output(outputs, "transferable_skill_level")
    if not actual_transferable_skill_level:
        actual_transferable_skill_level = _normalized_output(outputs, "transferable_skills")
    expected_transferable_skill_level = _normalized_output(reference, "expected_transferable_skill_level")

    fit_score = int(outputs.get("fit_score") or 0)
    hard_reject_expected = expected_deal_breaker_severity == "HARD" or expected_role_alignment == "LOW"
    hard_reject_penalty_applied = fit_score < 80 if hard_reject_expected else True

    return EvaluationResults(
        results=[
            EvaluationResult(
                key="role_alignment_match",
                score=1 if expected_role_alignment and actual_role_alignment == expected_role_alignment else 0,
                comment=f"expected={expected_role_alignment}, actual={actual_role_alignment}",
            ),
            EvaluationResult(
                key="must_have_coverage_match",
                score=1
                if expected_must_have_coverage and actual_must_have_coverage == expected_must_have_coverage
                else 0,
                comment=f"expected={expected_must_have_coverage}, actual={actual_must_have_coverage}",
            ),
            EvaluationResult(
                key="deal_breaker_severity_match",
                score=1
                if expected_deal_breaker_severity and actual_deal_breaker_severity == expected_deal_breaker_severity
                else 0,
                comment=f"expected={expected_deal_breaker_severity}, actual={actual_deal_breaker_severity}",
            ),
            EvaluationResult(
                key="transferable_skill_credit",
                score=1
                if expected_transferable_skill_level
                and actual_transferable_skill_level == expected_transferable_skill_level
                else 0,
                comment=f"expected={expected_transferable_skill_level}, actual={actual_transferable_skill_level}",
            ),
            EvaluationResult(
                key="hard_reject_penalty",
                score=1 if hard_reject_penalty_applied else 0,
                comment=(
                    f"fit_score={fit_score}, expected_role_alignment={expected_role_alignment}, "
                    f"expected_deal_breaker_severity={expected_deal_breaker_severity}, "
                    f"hard_reject_expected={hard_reject_expected}"
                ),
            ),
        ]
    )


def evaluate_reasoning_quality(run, example=None):
    del example
    outputs = (run.outputs or {}) if run else {}
    summary = str(outputs.get("summary") or outputs.get("reasoning") or "").strip()
    line_count = len([line for line in summary.splitlines() if line.strip()])
    return EvaluationResult(
        key="summary_concise",
        score=1 if summary and line_count <= 3 else 0,
        comment=f"line_count={line_count}, has_summary={bool(summary)}",
    )


def evaluate_signal_alignment(run, example=None):
    outputs = (run.outputs or {}) if run else {}
    reference = (example.outputs or {}) if example else {}
    actual_must_haves = set(outputs.get("must_have_matches") or outputs.get("must_have_hits") or [])
    expected_must_haves = set(reference.get("expected_must_have_matches") or [])
    actual_deal_breakers = set(outputs.get("deal_breaker_flags") or outputs.get("deal_breakers_found") or [])
    expected_deal_breakers = set(reference.get("expected_deal_breaker_flags") or [])
    return EvaluationResults(
        results=[
            EvaluationResult(
                key="must_have_expectation",
                score=1 if expected_must_haves.issubset(actual_must_haves) else 0,
                comment=f"expected={sorted(expected_must_haves)}, actual={sorted(actual_must_haves)}",
            ),
            EvaluationResult(
                key="deal_breaker_expectation",
                score=1 if expected_deal_breakers.issubset(actual_deal_breakers) else 0,
                comment=f"expected={sorted(expected_deal_breakers)}, actual={sorted(actual_deal_breakers)}",
            ),
        ]
    )


def evaluate_structured_explanations(run, example=None):
    outputs = (run.outputs or {}) if run else {}
    reference = (example.outputs or {}) if example else {}

    actual_strengths = " ".join(str(item) for item in (outputs.get("strengths") or []))
    actual_concerns = " ".join(str(item) for item in (outputs.get("concerns") or []))
    expected_strengths = [str(item).lower() for item in (reference.get("expected_strength_keywords") or [])]
    expected_concerns = [str(item).lower() for item in (reference.get("expected_concern_keywords") or [])]
    actual_confidence = str(outputs.get("confidence") or "").upper()
    expected_confidence = str(reference.get("expected_confidence") or "").upper()

    strengths_match = all(keyword in actual_strengths.lower() for keyword in expected_strengths)
    concerns_match = all(keyword in actual_concerns.lower() for keyword in expected_concerns)

    return EvaluationResults(
        results=[
            EvaluationResult(
                key="strength_keywords_match",
                score=1 if strengths_match else 0,
                comment=f"expected={expected_strengths}, actual={actual_strengths}",
            ),
            EvaluationResult(
                key="concern_keywords_match",
                score=1 if concerns_match else 0,
                comment=f"expected={expected_concerns}, actual={actual_concerns}",
            ),
            EvaluationResult(
                key="confidence_alignment",
                score=1 if not expected_confidence or actual_confidence == expected_confidence else 0,
                comment=f"expected={expected_confidence}, actual={actual_confidence}",
            ),
        ]
    )


RULE_BASED_EVALUATORS = [
    evaluate_job_match,
    evaluate_fit_score_band,
    evaluate_score_policy_alignment,
    evaluate_reasoning_quality,
    evaluate_signal_alignment,
    evaluate_structured_explanations,
]
