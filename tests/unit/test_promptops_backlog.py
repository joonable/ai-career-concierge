from promptops.core.failures import FAILURE_TAXONOMY, build_failure_record
from promptops.projects.ai_career_concierge.backlog_rules import build_backlog_candidates_from_review
from promptops.core.models import ReviewFeedbackRecord


def test_failure_taxonomy_is_defined_for_promptops_routing():
    assert FAILURE_TAXONOMY["prompt.role_alignment"]
    assert FAILURE_TAXONOMY["dataset.borderline_coverage_gap"]
    assert FAILURE_TAXONOMY["feature.onboarding_signal_missing"]


def test_review_feedback_maps_to_external_backlog_candidate_keys():
    feedback = ReviewFeedbackRecord(
        review_item_id="review-1",
        reviewer_type="human",
        scores={
            "role_alignment": "incorrect",
            "must_have_coverage": "incorrect",
            "deal_breaker_handling": "correct",
            "transferable_skill_credit": "low",
            "summary_usefulness": "correct",
        },
        notes="Borderline platform role is still being over-scored.",
        decision="revise_prompt",
    )

    candidates = build_backlog_candidates_from_review(feedback)

    assert candidates == [
        "prompt:role-alignment",
        "prompt:must-have-coverage",
        "prompt:transferable-skill-credit",
    ]


def test_failure_record_can_be_built_for_non_prompt_categories():
    failure = build_failure_record(
        taxonomy_key="feature.onboarding_signal_missing",
        category="feature",
        summary="User intent for platform-heavy roles is missing.",
        evidence=["Need a stronger onboarding preference for adjacent ML platform roles."],
        source_review_item_id="review-2",
    )

    assert failure.taxonomy_key == "feature.onboarding_signal_missing"
    assert failure.category == "feature"
    assert failure.source_review_item_id == "review-2"
