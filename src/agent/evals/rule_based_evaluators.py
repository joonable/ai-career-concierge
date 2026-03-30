from __future__ import annotations

from typing import Any, Dict, List

from langsmith.evaluation.evaluator import EvaluationResult, EvaluationResults


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


def evaluate_reasoning_quality(run, example=None):
    del example
    outputs = (run.outputs or {}) if run else {}
    reasoning = str(outputs.get("reasoning") or "").strip()
    line_count = len([line for line in reasoning.splitlines() if line.strip()])
    return EvaluationResult(
        key="reasoning_concise",
        score=1 if reasoning and line_count <= 3 else 0,
        comment=f"line_count={line_count}, has_reasoning={bool(reasoning)}",
    )


def evaluate_signal_alignment(run, example=None):
    outputs = (run.outputs or {}) if run else {}
    reference = (example.outputs or {}) if example else {}
    actual_must_haves = set(outputs.get("must_have_hits") or [])
    expected_must_haves = set(reference.get("expected_must_have_hits") or [])
    actual_deal_breakers = set(outputs.get("deal_breakers_found") or [])
    expected_deal_breakers = set(reference.get("expected_deal_breakers_found") or [])
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


RULE_BASED_EVALUATORS = [
    evaluate_job_match,
    evaluate_fit_score_band,
    evaluate_reasoning_quality,
    evaluate_signal_alignment,
]
