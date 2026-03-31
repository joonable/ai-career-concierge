from __future__ import annotations

from promptops.core.models import ReviewFeedbackRecord, ReviewQueueSpec, ReviewRubricCriterion


HUMAN_REVIEW_RUBRIC = [
    ReviewRubricCriterion(
        key="role_alignment",
        label="Role alignment",
        description="Does the job's actual responsibility set match the target role closely enough?",
    ),
    ReviewRubricCriterion(
        key="must_have_coverage",
        label="Must-have coverage",
        description="Are the user's required conditions actually evidenced strongly enough?",
    ),
    ReviewRubricCriterion(
        key="deal_breaker_handling",
        label="Deal-breaker handling",
        description="Did the evaluation correctly identify and weight deal-breakers?",
    ),
    ReviewRubricCriterion(
        key="transferable_skill_credit",
        label="Transferable skill credit",
        description="Did the evaluation give appropriate credit to adjacent but relevant experience?",
    ),
    ReviewRubricCriterion(
        key="summary_usefulness",
        label="Summary usefulness",
        description="Is the explanation concise and useful for a human reviewer or end user?",
    ),
]


DEFAULT_REVIEW_QUEUE = ReviewQueueSpec(
    queue_name="job-evaluation-review",
    prompt_family="job-evaluation",
    queue_mode="single",
    backend="langsmith",
    rubric_keys=[criterion.key for criterion in HUMAN_REVIEW_RUBRIC],
    description="Borderline and failed job-evaluation cases for human review.",
)


def classify_feedback_outcome(feedback: ReviewFeedbackRecord) -> list[str]:
    """Map review feedback to backlog candidate buckets.

    This stays project-specific because the meaning of each rubric score is
    tied to job recommendation quality.
    """

    backlog: list[str] = []
    if feedback.scores.get("role_alignment") in {"low", "incorrect"}:
        backlog.append("prompt:role-alignment")
    if feedback.scores.get("must_have_coverage") in {"low", "incorrect"}:
        backlog.append("prompt:must-have-coverage")
    if feedback.scores.get("deal_breaker_handling") in {"low", "incorrect"}:
        backlog.append("policy:deal-breaker-handling")
    if feedback.scores.get("transferable_skill_credit") in {"low", "incorrect"}:
        backlog.append("prompt:transferable-skill-credit")
    if feedback.scores.get("summary_usefulness") in {"low", "incorrect"}:
        backlog.append("prompt:summary-usefulness")
    return backlog
