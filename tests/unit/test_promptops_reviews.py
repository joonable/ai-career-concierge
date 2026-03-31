from promptops.adapters.langsmith import LangSmithPromptOpsAdapter
from promptops.core.failures import is_borderline_case, is_failure_case
from promptops.core.reviews import create_feedback_record, create_review_item, queue_supports_item
from promptops.core.models import ReviewQueueSpec
from promptops.projects.ai_career_concierge.backlog_rules import build_backlog_candidates_from_review
from promptops.projects.ai_career_concierge.review_rubric import DEFAULT_REVIEW_QUEUE, HUMAN_REVIEW_RUBRIC


def test_review_rubric_and_queue_are_defined_for_job_evaluation():
    assert DEFAULT_REVIEW_QUEUE.queue_name == "job-evaluation-review"
    assert DEFAULT_REVIEW_QUEUE.prompt_family == "job-evaluation"
    assert [criterion.key for criterion in HUMAN_REVIEW_RUBRIC] == [
        "role_alignment",
        "must_have_coverage",
        "deal_breaker_handling",
        "transferable_skill_credit",
        "summary_usefulness",
    ]


def test_review_item_and_feedback_record_capture_review_contract():
    item = create_review_item(
        item_id="review-1",
        prompt_family="job-evaluation",
        experiment_id="experiment-1",
        run_id="run-1",
        dataset_example_id="gold-005",
        queue_name="job-evaluation-review",
        mode="human",
        reasons=["borderline_case", "fit_score_band_miss"],
    )
    feedback = create_feedback_record(
        review_item_id=item.item_id,
        reviewer_type="human",
        reviewer_id="joon",
        scores={
            "role_alignment": "incorrect",
            "must_have_coverage": "correct",
            "deal_breaker_handling": "correct",
            "transferable_skill_credit": "low",
            "summary_usefulness": "correct",
        },
        decision="revise_prompt",
        notes="Borderline infra role is still over-credited.",
    )

    assert item.status == "pending"
    assert "fit_score_band_miss" in item.reasons
    assert feedback.decision == "revise_prompt"
    assert build_backlog_candidates_from_review(feedback) == [
        "prompt:role-alignment",
        "prompt:transferable-skill-credit",
    ]


def test_failure_and_borderline_selection_rules_are_defined():
    assert is_borderline_case(fit_score=50, role_alignment="MEDIUM") is True
    assert is_borderline_case(fit_score=91, role_alignment="HIGH") is False
    assert is_failure_case(evaluator_scores={"fit_score_band": 0.0, "classification_match": 1.0}) is True
    assert is_failure_case(evaluator_scores={"fit_score_band": 1.0}) is False


def test_langsmith_review_payloads_follow_queue_and_feedback_contract():
    adapter = LangSmithPromptOpsAdapter(
        client=object(),
        settings=type(
            "Settings",
            (),
            {
                "langsmith_api_key": "test-key",
                "gemini_model": "gemini-test",
                "langsmith_eval_prompt_identifier": "job-evaluation:staging",
                "langsmith_eval_prompt_version": "local-v3",
            },
        )(),
        workspace_id="workspace-123",
    )
    queue = ReviewQueueSpec(
        queue_name="job-evaluation-review",
        prompt_family="job-evaluation",
        queue_mode="single",
        backend="langsmith",
        rubric_keys=["role_alignment", "must_have_coverage"],
        description="Borderline review queue",
    )
    item = create_review_item(
        item_id="review-1",
        prompt_family="job-evaluation",
        experiment_id="experiment-1",
        run_id="run-1",
        queue_name="job-evaluation-review",
        reasons=["borderline_case"],
    )
    feedback = create_feedback_record(
        review_item_id="review-1",
        reviewer_type="human",
        scores={"role_alignment": "correct"},
        decision="approve",
    )

    assert queue_supports_item(queue, item) is True
    queue_payload = adapter.build_annotation_queue_payload(queue=queue, items=[item])
    feedback_payload = adapter.build_feedback_payload(feedback)

    assert queue_payload["queue_name"] == "job-evaluation-review"
    assert queue_payload["items"][0]["run_id"] == "run-1"
    assert feedback_payload["review_item_id"] == "review-1"
