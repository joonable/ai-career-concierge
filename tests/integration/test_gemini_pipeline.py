from contextlib import contextmanager

import httpx
from sqlmodel import select

from api.services.gemini_evaluator import GeminiEvaluator
from db.enums import EvaluationStatus
from db.models import Evaluation, SystemLog


class RecordingRunHandle:
    def __init__(self) -> None:
        self.outputs = None
        self.metadata = {}

    def set_outputs(self, outputs):
        self.outputs = outputs

    def add_metadata(self, metadata):
        self.metadata.update(metadata)


class RecordingTracer:
    def __init__(self) -> None:
        self.app_env = "test"
        self.project_name = "ai-career-concierge-test"
        self.pipeline_runs = []
        self.llm_runs = []

    @contextmanager
    def pipeline_run(self, *, run_id, user_id, dry_run, app_env):
        handle = RecordingRunHandle()
        self.pipeline_runs.append(
            {
                "run_id": run_id,
                "user_id": user_id,
                "dry_run": dry_run,
                "app_env": app_env,
                "handle": handle,
            }
        )
        yield handle

    @contextmanager
    def llm_run(self, *, name, inputs, metadata, tags):
        handle = RecordingRunHandle()
        self.llm_runs.append(
            {
                "name": name,
                "inputs": inputs,
                "metadata": metadata,
                "tags": tags,
                "handle": handle,
            }
        )
        yield handle


async def test_pipeline_with_gemini_evaluator_persists_llm_results(client, db_session, app):
    from tests.conftest import StaticScraper, ValidGeminiTransport, build_runtime, seed_user

    from api.dependencies.runtime import get_runtime

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
    from tests.conftest import FailingGeminiTransport, StaticScraper, build_runtime, seed_user

    from api.dependencies.runtime import get_runtime

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


async def test_pipeline_records_langsmith_root_and_llm_traces(client, db_session, app):
    from tests.conftest import StaticScraper, ValidGeminiTransport, build_runtime, seed_user

    from api.dependencies.runtime import get_runtime

    tracer = RecordingTracer()
    http_client = httpx.AsyncClient(transport=httpx.MockTransport(ValidGeminiTransport()))
    runtime = build_runtime(
        scrapers=[StaticScraper()],
        evaluator=GeminiEvaluator(api_key="test-key", http_client=http_client),
        tracer=tracer,
    )
    app.dependency_overrides[get_runtime] = lambda: runtime
    user = seed_user(db_session)

    response = await client.post(
        "/api/v1/pipeline/trigger",
        headers={"X-API-Key": "test-internal-key"},
        json={},
    )

    assert response.status_code == 200
    assert len(tracer.pipeline_runs) == 1
    assert tracer.pipeline_runs[0]["user_id"] == str(user.id)
    assert tracer.pipeline_runs[0]["handle"].metadata["pipeline_version"] == "test-v1"
    assert tracer.pipeline_runs[0]["handle"].outputs["jobs_ingested"] >= 1
    assert len(tracer.llm_runs) >= 1
    assert tracer.llm_runs[0]["name"] == "gemini.evaluate"
    assert tracer.llm_runs[0]["metadata"]["prompt_name"] == "job-evaluation"
    assert tracer.llm_runs[0]["handle"].metadata["model"] == "gemini-2.0-flash"
    assert "rendered_prompt" in tracer.llm_runs[0]["inputs"]
    await http_client.aclose()
