from __future__ import annotations

from promptops.core.backlog import build_backlog_item
from promptops.core.failures import build_failure_record
from promptops.core.models import BacklogItem, ReviewFeedbackRecord
from promptops.projects.ai_career_concierge.review_rubric import classify_feedback_outcome


def build_backlog_candidates_from_review(feedback: ReviewFeedbackRecord) -> list[str]:
    """Translate review feedback into PromptOps backlog candidate keys."""

    return classify_feedback_outcome(feedback)


def build_backlog_items_from_review(feedback: ReviewFeedbackRecord) -> list[BacklogItem]:
    """Convert review feedback into actionable backlog items."""

    items: list[BacklogItem] = []
    for candidate in classify_feedback_outcome(feedback):
        category, name = candidate.split(":", 1)
        taxonomy_key = _taxonomy_key_for_candidate(candidate)
        failure = build_failure_record(
            taxonomy_key=taxonomy_key,
            category=category,
            summary=f"Review flagged {name.replace('-', ' ')}.",
            evidence=[feedback.notes] if feedback.notes else [],
            source_review_item_id=feedback.review_item_id,
        )
        items.append(
            build_backlog_item(
                item_key=candidate,
                category=category,
                title=_title_for_candidate(candidate),
                action=_action_for_candidate(candidate),
                linked_failures=[failure],
            )
        )
    return items


def example_failure_backlog_items() -> list[BacklogItem]:
    """Return representative failure examples for PromptOps operations docs."""

    examples = [
        ("prompt:role-alignment", "Adjacent infra role is scored one band too high."),
        ("prompt:must-have-coverage", "Must-have gaps are explained but not penalized enough."),
        ("policy:deal-breaker-handling", "Hard blocker is identified but score stays too permissive."),
        ("dataset:borderline-coverage-gap", "Gold set lacks enough ML-adjacent infra cases."),
        ("feature:onboarding-signal-missing", "User intent about platform-heavy roles is not collected."),
    ]
    items: list[BacklogItem] = []
    for key, evidence in examples:
        category, _ = key.split(":", 1)
        taxonomy_key = _taxonomy_key_for_candidate(key)
        failure = build_failure_record(
            taxonomy_key=taxonomy_key,
            category=category,
            summary=evidence,
            evidence=[evidence],
        )
        items.append(
            build_backlog_item(
                item_key=key,
                category=category,
                title=_title_for_candidate(key),
                action=_action_for_candidate(key),
                linked_failures=[failure],
            )
        )
    return items


def _taxonomy_key_for_candidate(candidate: str) -> str:
    return {
        "prompt:role-alignment": "prompt.role_alignment",
        "prompt:must-have-coverage": "prompt.must_have_coverage",
        "prompt:transferable-skill-credit": "prompt.transferable_skill_credit",
        "prompt:summary-usefulness": "prompt.summary_usefulness",
        "dataset:borderline-coverage-gap": "dataset.borderline_coverage_gap",
        "dataset:gold-expectation-gap": "dataset.gold_expectation_gap",
        "policy:deal-breaker-handling": "policy.deal_breaker_handling",
        "policy:score-band-definition": "policy.score_band_definition",
        "context:normalization-gap": "context.normalization_gap",
        "feature:onboarding-signal-missing": "feature.onboarding_signal_missing",
    }[candidate]


def _title_for_candidate(candidate: str) -> str:
    return {
        "prompt:role-alignment": "Refine role-alignment guidance in the evaluation prompt",
        "prompt:must-have-coverage": "Tighten must-have coverage guidance in the evaluation prompt",
        "prompt:transferable-skill-credit": "Adjust transferable skill credit wording for adjacent roles",
        "prompt:summary-usefulness": "Improve summary instructions for reviewer usefulness",
        "dataset:borderline-coverage-gap": "Add more borderline adjacent-role gold examples",
        "dataset:gold-expectation-gap": "Clarify gold expectations for ambiguous job families",
        "policy:deal-breaker-handling": "Clarify hard deal-breaker scoring policy",
        "policy:score-band-definition": "Document narrower score-band policy for borderline cases",
        "context:normalization-gap": "Add missing normalized context signal for evaluation",
        "feature:onboarding-signal-missing": "Collect missing onboarding signal needed for evaluation",
    }[candidate]


def _action_for_candidate(candidate: str) -> str:
    return {
        "prompt:role-alignment": "Update prompt wording and rerun the curated experiment.",
        "prompt:must-have-coverage": "Update prompt wording and add regression examples if needed.",
        "prompt:transferable-skill-credit": "Revise adjacent-role wording and validate on borderline cases.",
        "prompt:summary-usefulness": "Improve summary instruction and check reviewer usefulness.",
        "dataset:borderline-coverage-gap": "Add new borderline cases and resync the gold dataset.",
        "dataset:gold-expectation-gap": "Review and update expected outputs with a product decision note.",
        "policy:deal-breaker-handling": "Clarify policy in docs and prompt, then rerun the experiment.",
        "policy:score-band-definition": "Refine score band contract before additional prompt changes.",
        "context:normalization-gap": "Extend normalized context schema and add contract tests.",
        "feature:onboarding-signal-missing": "Add the missing feature to onboarding backlog before further tuning.",
    }[candidate]
