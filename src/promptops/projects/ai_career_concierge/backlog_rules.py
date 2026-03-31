from __future__ import annotations

from promptops.core.models import ReviewFeedbackRecord
from promptops.projects.ai_career_concierge.review_rubric import classify_feedback_outcome


def build_backlog_candidates_from_review(feedback: ReviewFeedbackRecord) -> list[str]:
    """Translate review feedback into PromptOps backlog candidate keys."""

    return classify_feedback_outcome(feedback)
