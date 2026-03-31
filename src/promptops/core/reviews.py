from __future__ import annotations

from promptops.core.models import ReviewFeedbackRecord, ReviewItem, ReviewQueueSpec


def create_review_item(
    *,
    item_id: str,
    prompt_family: str,
    experiment_id: str = "",
    run_id: str = "",
    dataset_example_id: str = "",
    queue_name: str = "",
    mode: str = "human",
    reasons: list[str] | None = None,
) -> ReviewItem:
    """Create a review item for human or LLM-judge workflows."""

    return ReviewItem(
        item_id=item_id,
        prompt_family=prompt_family,
        experiment_id=experiment_id,
        run_id=run_id,
        dataset_example_id=dataset_example_id,
        queue_name=queue_name,
        mode=mode,
        reasons=reasons or [],
    )


def create_feedback_record(
    *,
    review_item_id: str,
    reviewer_type: str,
    scores: dict[str, str],
    decision: str,
    notes: str = "",
    reviewer_id: str = "",
    backlog_candidates: list[str] | None = None,
) -> ReviewFeedbackRecord:
    """Create a persistable review feedback record."""

    return ReviewFeedbackRecord(
        review_item_id=review_item_id,
        reviewer_type=reviewer_type,
        reviewer_id=reviewer_id,
        scores=scores,
        decision=decision,
        notes=notes,
        backlog_candidates=backlog_candidates or [],
    )


def queue_supports_item(queue: ReviewQueueSpec, item: ReviewItem) -> bool:
    """Check if a review item belongs to a queue."""

    return queue.prompt_family == item.prompt_family and queue.queue_name == item.queue_name
