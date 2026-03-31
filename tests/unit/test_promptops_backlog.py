from promptops.core.backlog import backlog_priority_for_category
from promptops.core.failures import FAILURE_TAXONOMY, build_failure_record
from promptops.projects.ai_career_concierge.backlog_rules import (
    build_backlog_candidates_from_review,
    build_backlog_items_from_review,
    example_failure_backlog_items,
)
from promptops.core.models import ReviewFeedbackRecord


def test_failure_taxonomy_and_priority_defaults_are_defined():
    assert FAILURE_TAXONOMY["prompt.role_alignment"]
    assert FAILURE_TAXONOMY["dataset.borderline_coverage_gap"]
    assert backlog_priority_for_category("policy") == "P0"
    assert backlog_priority_for_category("feature") == "P1"
    assert backlog_priority_for_category("dataset") == "P2"


def test_review_feedback_maps_to_taxonomy_and_backlog_items():
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
    items = build_backlog_items_from_review(feedback)

    assert candidates == [
        "prompt:role-alignment",
        "prompt:must-have-coverage",
        "prompt:transferable-skill-credit",
    ]
    assert [item.item_key for item in items] == candidates
    assert all(item.priority == "P1" for item in items)
    assert items[0].linked_taxonomy_keys == ["prompt.role_alignment"]
    assert "Borderline platform role" in items[0].evidence[0]


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


def test_example_failure_backlog_items_register_five_examples():
    examples = example_failure_backlog_items()

    assert len(examples) == 5
    assert [item.item_key for item in examples] == [
        "prompt:role-alignment",
        "prompt:must-have-coverage",
        "policy:deal-breaker-handling",
        "dataset:borderline-coverage-gap",
        "feature:onboarding-signal-missing",
    ]
