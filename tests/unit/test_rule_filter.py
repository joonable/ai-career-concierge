from tests.conftest import FakeEvaluationStore

from agent.nodes.rule_filter_node import RuleFilterNode
from agent.schemas.pipeline_job import PipelineJob
from db.enums import EvaluationStatus


async def test_rule_filter_marks_title_mismatch_as_rule_rejected(db_session):
    from tests.conftest import seed_user

    user = seed_user(db_session, role="Machine Learning Engineer")
    store = FakeEvaluationStore(db_session)
    node = RuleFilterNode(evaluation_store=store)

    state = {
        "user_context": {
            "user_id": str(user.id),
            "profile_data": user.profile_data,
        },
        "current_jobs": [
            PipelineJob(
                job_id="f4f5620a-fde3-428a-b687-d2bde80ea81d",
                platform="test_source",
                external_job_id="job-001",
                title="Sales Operations Manager",
                company="Wrong Fit Inc.",
                jd_raw_text="Manage sales reporting.",
                url="https://example.com/job-001",
            )
        ],
    }

    result = await node.run(state)

    assert result["current_jobs"] == []
    evaluation = store.get_by_user_and_job(user.id, state["current_jobs"][0].job_id)
    assert evaluation is not None
    assert evaluation.status == EvaluationStatus.RULE_REJECTED
    assert evaluation.rule_rejection_reason == "TITLE_MISMATCH"


async def test_rule_filter_rejects_jobs_when_structured_location_preference_mismatches(db_session):
    from tests.conftest import seed_user

    user = seed_user(
        db_session,
        role="Machine Learning Engineer",
        preferences={"locations": ["seoul"]},
    )
    store = FakeEvaluationStore(db_session)
    node = RuleFilterNode(evaluation_store=store)

    state = {
        "user_context": {
            "user_id": str(user.id),
            "profile_data": user.profile_data,
            "preferences": user.preferences,
        },
        "current_jobs": [
            PipelineJob(
                job_id="7b8d5f30-e64d-4d5f-bec8-cd1d8d3374d4",
                platform="test_source",
                external_job_id="job-002",
                title="Senior Machine Learning Engineer",
                company="Remote Labs",
                jd_raw_text="Remote role based in Busan.",
                url="https://example.com/job-002",
                source_metadata={"location": "Busan"},
            )
        ],
    }

    result = await node.run(state)

    assert result["current_jobs"] == []
    evaluation = store.get_by_user_and_job(user.id, state["current_jobs"][0].job_id)
    assert evaluation is not None
    assert evaluation.status == EvaluationStatus.RULE_REJECTED
    assert evaluation.rule_rejection_reason == "LOCATION_MISMATCH"
