from sqlmodel import select

from db.enums import EvaluationStatus
from db.models import Evaluation, SystemLog


async def test_pipeline_continues_when_one_scraper_fails(client, db_session, app):
    from tests.conftest import FailingScraper, StaticScraper, build_runtime, seed_user

    from api.dependencies.runtime import get_runtime

    runtime = build_runtime(scrapers=[FailingScraper(), StaticScraper()])
    app.dependency_overrides[get_runtime] = lambda: runtime
    seed_user(db_session)

    response = await client.post(
        "/api/v1/pipeline/trigger",
        headers={"X-API-Key": "test-internal-key"},
        json={},
    )

    assert response.status_code == 200
    assert response.json()["runs"][0]["source_errors"] == ["broken_source"]
    assert len(runtime.slack_notifier.deliveries) == 1


async def test_invalid_llm_output_is_logged_and_keeps_evaluation_pending(client, db_session, app):
    from tests.conftest import InvalidEvaluator, StaticScraper, build_runtime, seed_user

    from api.dependencies.runtime import get_runtime

    runtime = build_runtime(scrapers=[StaticScraper()], evaluator=InvalidEvaluator())
    app.dependency_overrides[get_runtime] = lambda: runtime
    user = seed_user(db_session)

    response = await client.post(
        "/api/v1/pipeline/trigger",
        headers={"X-API-Key": "test-internal-key"},
        json={},
    )

    assert response.status_code == 200
    assert response.json()["runs"][0]["jobs_sent"] == 0

    evaluations = db_session.exec(select(Evaluation).where(Evaluation.user_id == user.id)).all()
    assert any(evaluation.status == EvaluationStatus.PENDING for evaluation in evaluations)

    logs = db_session.exec(select(SystemLog)).all()
    assert any(log.event_type == "llm_eval_invalid_output" for log in logs)
