from sqlmodel import select

from db.models import Evaluation, Job


async def test_pipeline_trigger_validates_internal_api_key(client, db_session):
    from tests.conftest import seed_user

    seed_user(db_session)
    response = await client.post(
        "/api/v1/pipeline/trigger",
        headers={"X-API-Key": "wrong-key"},
        json={},
    )

    assert response.status_code == 401


async def test_pipeline_trigger_runs_end_to_end(client, db_session, runtime):
    from tests.conftest import seed_user

    runtime.slack_notifier.deliveries.clear()
    seed_user(db_session)

    response = await client.post(
        "/api/v1/pipeline/trigger",
        headers={"X-API-Key": "test-internal-key"},
        json={},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["runs"]) == 1
    assert body["runs"][0]["jobs_sent"] == 1
    assert runtime.slack_notifier.deliveries

    evaluations = db_session.exec(select(Evaluation)).all()
    jobs = db_session.exec(select(Job)).all()
    assert len(jobs) == 2
    assert len(evaluations) == 2
