from pathlib import Path

from agent.evals.dataset_workflow import load_curated_examples
from agent.evals.rule_based_evaluators import (
    evaluate_fit_score_band,
    evaluate_score_policy_alignment,
    evaluate_signal_alignment,
    evaluate_structured_explanations,
)


def _result_map(evaluation_results) -> dict[str, object]:
    return {result.key: result for result in evaluation_results["results"]}


def test_borderline_fixture_examples_include_score_policy_metadata():
    examples = load_curated_examples(Path("src/agent/evals/fixtures/job_eval_gold.json"))

    borderline_examples = [
        example
        for example in examples
        if example["metadata"]["scenario_type"] == "borderline_case"
    ]

    assert len(borderline_examples) >= 8
    assert all(example["metadata"]["scenario_family"] for example in borderline_examples)
    assert all(example["outputs"]["scoring_note"] for example in borderline_examples)
    assert all(
        example["outputs"]["expected_role_alignment"] in {"HIGH", "MEDIUM", "LOW"}
        for example in borderline_examples
    )
    assert all(
        example["outputs"]["expected_must_have_coverage"] in {"STRONG", "PARTIAL", "WEAK"}
        for example in borderline_examples
    )
    assert all(
        example["outputs"]["expected_deal_breaker_severity"] in {"NONE", "SOFT", "HARD"}
        for example in borderline_examples
    )
    assert all(
        example["outputs"]["expected_transferable_skill_level"] in {"HIGH", "MEDIUM", "LOW"}
        for example in borderline_examples
    )


def test_borderline_regression_is_decomposed_when_fit_score_band_misses():
    examples = load_curated_examples(Path("src/agent/evals/fixtures/job_eval_gold.json"))
    borderline_example = next(
        example
        for example in examples
        if example["inputs"]["job"]["external_job_id"] == "gold-005"
    )

    class Run:
        outputs = {
            "fit_score": 30,
            "summary": "Adjacent data skill overlap exists\nBut core MLOps ownership is missing",
            "strengths": ["Strong Python and SQL overlap", "Relevant data pipeline background"],
            "concerns": ["Missing MLOps ownership", "No model serving responsibility"],
            "must_have_matches": ["Python", "SQL"],
            "deal_breaker_flags": [],
            "confidence": "MEDIUM",
            "role_alignment": "MEDIUM",
            "must_have_coverage": "PARTIAL",
            "deal_breaker_severity": "NONE",
            "transferable_skills": "HIGH",
        }

    class Example:
        outputs = borderline_example["outputs"]

    fit_score_result = evaluate_fit_score_band(Run(), Example())
    score_policy_results = _result_map(evaluate_score_policy_alignment(Run(), Example()))
    signal_results = _result_map(evaluate_signal_alignment(Run(), Example()))
    explanation_results = _result_map(evaluate_structured_explanations(Run(), Example()))

    assert fit_score_result.score == 0
    assert score_policy_results["role_alignment_match"].score == 1
    assert score_policy_results["must_have_coverage_match"].score == 1
    assert score_policy_results["deal_breaker_severity_match"].score == 1
    assert score_policy_results["transferable_skill_credit"].score == 1
    assert score_policy_results["hard_reject_penalty"].score == 1
    assert signal_results["must_have_expectation"].score == 1
    assert signal_results["deal_breaker_expectation"].score == 1
    assert explanation_results["concern_keywords_match"].score == 1
    assert explanation_results["confidence_alignment"].score == 1
