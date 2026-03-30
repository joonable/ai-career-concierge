import httpx
from sqlmodel import select

from api.services.gemini_evaluator import GeminiEvaluator
from db.enums import EvaluationStatus
from db.models import Evaluation, SystemLog


async def test_pipeline_with_gemini_evaluator_persists_llm_results(client, db_session, app):
    from api.dependencies.runtime import get_runtime
    from tests.conftest import StaticScraper, ValidGeminiTransport, build_runtime, seed_user

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(ValidGeminiTransport()))
    runtime = build_runtime(
        scrapers=[StaticScraper()],
        evaluator=GeminiEvaluator(api_key="test-key", http_client=http_client),
    )
    app.dependency_overrides[get_runtime] = lambda: runtime
    user = seed_user(db_session)

    response = await client.post(
        "/api/v1/pipeline/trigger",
        headers={"X-API-Key": "test-internal-key"},
        json={},
    )

    assert response.status_code == 200
    evaluations = db_session.exec(select(Evaluation).where(Evaluation.user_id == user.id)).all()
    assert any(evaluation.status == EvaluationStatus.LLM_EVALUATED for evaluation in evaluations)
    assert any(evaluation.fit_score == 91 for evaluation in evaluations)
    await http_client.aclose()


async def test_pipeline_logs_provider_failures_from_gemini_evaluator(client, db_session, app):
    from api.dependencies.runtime import get_runtime
    from tests.conftest import FailingGeminiTransport, StaticScraper, build_runtime, seed_user

    http_client = httpx.AsyncClient(transport=httpx.MockTransport(FailingGeminiTransport()))
    runtime = build_runtime(
        scrapers=[StaticScraper()],
        evaluator=GeminiEvaluator(api_key="test-key", http_client=http_client),
    )
    app.dependency_overrides[get_runtime] = lambda: runtime
    user = seed_user(db_session)

    response = await client.post(
        "/api/v1/pipeline/trigger",
        headers={"X-API-Key": "test-internal-key"},
        json={},
    )

    assert response.status_code == 200

    evaluations = db_session.exec(select(Evaluation).where(Evaluation.user_id == user.id)).all()
    assert any(evaluation.status == EvaluationStatus.PENDING for evaluation in evaluations)

    logs = db_session.exec(select(SystemLog)).all()
    assert any(log.event_type == "llm_eval_failure" for log in logs)
    await http_client.aclose()
