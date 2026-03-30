from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Iterable, List, Optional

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, SQLModel, create_engine

from agent.schemas.pipeline_job import PipelineJob
from agent.prompts import PromptManager
from api.schemas.users import build_user_profile_response, serialize_user_profile_sections
from api.services.gemini_evaluator import GeminiEvaluator
from api.services.mock_llm_evaluator import MockGeminiEvaluator
from api.services.runtime import RuntimeServices
from api.services.slack_notifier import LoggingSlackNotifier
from api.services.slack_signature_service import SlackSignatureService
from api.services.supabase_storage import DashboardRow, EvaluationRecord, FeedbackRecord
from common.config import get_settings
from common.telemetry import LangSmithTracer
from db.enums import EvaluationStatus, FeedbackState, LogLevel
from db.models import Evaluation, Job, User
from db.repositories import EvaluationRepository, JobRepository, SystemLogRepository, UserRepository
from db.session import get_engine
from scraper.base import ScrapedJob
from scraper.registry import ScraperRegistry


class StaticScraper:
    def __init__(self, source_name: str = "test_source", jobs: Optional[List[ScrapedJob]] = None):
        self.source_name = source_name
        self._jobs = jobs or [
            ScrapedJob(
                platform=source_name,
                external_job_id="test-001",
                title="Senior Machine Learning Engineer",
                company="Signal Labs",
                jd_raw_text="Python SQL recommender systems and ML platform ownership.",
                url="https://example.com/jobs/test-001",
                min_years_experience=5,
                max_years_experience=8,
            ),
            ScrapedJob(
                platform=source_name,
                external_job_id="test-002",
                title="Junior Frontend Engineer",
                company="Noise Portal",
                jd_raw_text="Pure marketing frontend work.",
                url="https://example.com/jobs/test-002",
                min_years_experience=0,
                max_years_experience=2,
            ),
        ]

    async def fetch_jobs(self, user_context):
        del user_context
        return self._jobs


class FailingScraper:
    source_name = "broken_source"

    async def fetch_jobs(self, user_context):
        del user_context
        raise RuntimeError("scraper exploded")


class InvalidEvaluator:
    async def evaluate(
        self,
        *,
        job,
        prompt,
        user_context,
        recent_memory,
        prompt_metadata=None,
        evaluation_id=None,
    ):
        del job
        del prompt
        del user_context
        del recent_memory
        del prompt_metadata
        del evaluation_id
        return {
            "fit_score": 999,
            "reasoning": "invalid output",
            "must_have_hits": [],
            "deal_breakers_found": [],
        }


class FailingGeminiTransport:
    def __call__(self, request):
        import httpx

        del request
        return httpx.Response(500, json={"error": {"message": "provider unavailable"}})


class ValidGeminiTransport:
    def __call__(self, request):
        import httpx

        del request
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": (
                                        '{"fit_score": 91, "reasoning": "Strong ML systems fit\\n'
                                        'Matches must-have stack", "must_have_hits": ["Python", "SQL"], '
                                        '"deal_breakers_found": []}'
                                    )
                                }
                            ]
                        }
                    }
                ]
            },
        )


class FakeTokenVerifier:
    def verify_access_token(self, token: str):
        if token != "test-supabase-token":
            raise ValueError("bad token")

        from api.dependencies.auth import UserIdentity

        return UserIdentity(
            user_id="89b6698f-d88b-4b83-baa8-23a3a8ee7f92",
            email="scaffold-user@example.com",
            oauth_id="89b6698f-d88b-4b83-baa8-23a3a8ee7f92",
        )


class FakeUserStore:
    def __init__(self, session: Session):
        self.repo = UserRepository(session)

    def upsert_from_identity(self, identity):
        user = self.repo.upsert_from_identity(
            email=identity.email,
            oauth_id=identity.oauth_id,
            preferred_user_id=identity.user_id,
        )
        profile = build_user_profile_response(
            user_id=user.id,
            email=user.email,
            profile_data=user.profile_data,
            guidelines=user.guidelines,
            notification_settings=user.notification_settings,
        )
        sections = serialize_user_profile_sections(profile)
        if (
            user.profile_data != sections["profile_data"]
            or user.guidelines != sections["guidelines"]
            or user.notification_settings != sections["notification_settings"]
        ):
            user = self.repo.update_profile(
                user=user,
                profile_data=sections["profile_data"],
                guidelines=sections["guidelines"],
                notification_settings=sections["notification_settings"],
            )
            profile = build_user_profile_response(
                user_id=user.id,
                email=user.email,
                profile_data=user.profile_data,
                guidelines=user.guidelines,
                notification_settings=user.notification_settings,
            )
        return profile

    def update_profile(self, identity, payload):
        user = self.repo.upsert_from_identity(
            email=identity.email,
            oauth_id=identity.oauth_id,
            preferred_user_id=identity.user_id,
        )
        sections = serialize_user_profile_sections(payload)
        updated = self.repo.update_profile(
            user=user,
            profile_data=sections["profile_data"],
            guidelines=sections["guidelines"],
            notification_settings=sections["notification_settings"],
        )
        identity.user_id = updated.id
        return self.upsert_from_identity(identity)

    def get_user_by_id(self, user_id):
        user = self.repo.get_by_id(user_id)
        if user is None:
            return None
        from api.dependencies.auth import UserIdentity

        return self.upsert_from_identity(
            UserIdentity(
                user_id=user.id,
                email=user.email,
                oauth_id=user.oauth_id,
            )
        )

    def list_all_users(self):
        from api.dependencies.auth import UserIdentity

        return [
            self.upsert_from_identity(
                UserIdentity(
                    user_id=user.id,
                    email=user.email,
                    oauth_id=user.oauth_id,
                )
            )
            for user in self.repo.list_all()
        ]


class FakeEvaluationStore:
    def __init__(self, session: Session):
        self.repo = EvaluationRepository(session)

    def list_dashboard_rows(self, user_id):
        rows = self.repo.list_dashboard_rows(user_id)
        return [
            DashboardRow(
                evaluation_id=evaluation.id,
                status=evaluation.status.value if hasattr(evaluation.status, "value") else evaluation.status,
                fit_score=evaluation.fit_score,
                reasoning=evaluation.reasoning,
                rule_rejection_reason=evaluation.rule_rejection_reason,
                user_feedback=(
                    evaluation.user_feedback.value
                    if getattr(evaluation.user_feedback, "value", None)
                    else evaluation.user_feedback
                ),
                feedback_reason=evaluation.feedback_reason,
                created_at=evaluation.created_at,
                updated_at=evaluation.updated_at,
                job_id=job.id,
                title=job.title,
                company=job.company,
                url=job.url,
                platform=job.platform,
            )
            for evaluation, job in rows
        ]

    def get_by_user_and_job(self, user_id, job_id):
        evaluation = self.repo.get_by_user_and_job(user_id, job_id)
        if evaluation is None:
            return None
        return self._to_record(evaluation)

    def ensure_pending(self, user_id, job_id):
        return self._to_record(self.repo.ensure_pending(user_id=user_id, job_id=job_id))

    def mark_rule_rejected(self, user_id, job_id, reason):
        return self._to_record(self.repo.mark_rule_rejected(user_id=user_id, job_id=job_id, reason=reason))

    def mark_llm_evaluated(self, user_id, job_id, fit_score, reasoning):
        return self._to_record(
            self.repo.mark_llm_evaluated(
                user_id=user_id,
                job_id=job_id,
                fit_score=fit_score,
                reasoning=reasoning,
            )
        )

    def update_feedback(self, *, evaluation_id, feedback, feedback_reason, user_id=None):
        evaluation = self.repo.update_feedback(
            evaluation_id=evaluation_id,
            feedback=feedback,
            feedback_reason=feedback_reason,
        )
        if user_id is not None and evaluation.user_id != user_id:
            raise ValueError("Evaluation not found.")
        return FeedbackRecord(
            evaluation_id=evaluation.id,
            feedback=FeedbackState(
                evaluation.user_feedback.value
                if getattr(evaluation.user_feedback, "value", None)
                else evaluation.user_feedback
            ),
            feedback_reason=evaluation.feedback_reason,
        )

    def list_recent_dislikes(self, user_id, limit=10):
        return self.repo.list_recent_dislikes(user_id, limit=limit)

    @staticmethod
    def _to_record(evaluation):
        return EvaluationRecord(
            id=evaluation.id,
            user_id=evaluation.user_id,
            job_id=evaluation.job_id,
            status=(
                EvaluationStatus(evaluation.status.value)
                if getattr(evaluation.status, "value", None)
                else EvaluationStatus(evaluation.status)
            ),
            fit_score=evaluation.fit_score,
            reasoning=evaluation.reasoning,
            rule_rejection_reason=evaluation.rule_rejection_reason,
            user_feedback=(
                FeedbackState(evaluation.user_feedback.value)
                if getattr(evaluation.user_feedback, "value", None)
                else (FeedbackState(evaluation.user_feedback) if evaluation.user_feedback else None)
            ),
            feedback_reason=evaluation.feedback_reason,
        )


class FakeJobStore:
    def __init__(self, session: Session):
        self.repo = JobRepository(session)

    def upsert_job(self, scraped_job):
        job = self.repo.upsert_job(scraped_job)
        return PipelineJob(
            job_id=job.id,
            platform=job.platform,
            external_job_id=job.external_job_id,
            title=job.title,
            company=job.company,
            jd_raw_text=job.jd_raw_text,
            url=job.url,
            min_years_experience=job.min_years_experience,
            max_years_experience=job.max_years_experience,
            source_metadata=job.source_metadata,
        )


class FakeSystemLogStore:
    def __init__(self, session: Session):
        self.repo = SystemLogRepository(session)

    def create(self, *, run_id, event_type, message, level=LogLevel.INFO, user_id=None, job_id=None, platform=None, metadata=None):
        return self.repo.create(
            run_id=run_id,
            event_type=event_type,
            message=message,
            level=level,
            user_id=user_id,
            job_id=job_id,
            platform=platform,
            metadata=metadata,
        )


def build_runtime(
    *,
    scrapers: Optional[Iterable[object]] = None,
    evaluator: Optional[object] = None,
    notifier: Optional[LoggingSlackNotifier] = None,
    signing_secret: str = "dev-slack-secret",
    tracer: Optional[LangSmithTracer] = None,
    prompt_manager: Optional[PromptManager] = None,
) -> RuntimeServices:
    langsmith_tracer = tracer or LangSmithTracer.disabled()
    return RuntimeServices(
        scraper_registry=ScraperRegistry(scrapers or [StaticScraper()]),
        llm_evaluator=evaluator or MockGeminiEvaluator(),
        prompt_manager=prompt_manager
        or PromptManager(
            client=None,
            eval_prompt_identifier="",
            eval_prompt_name="job-evaluation",
            eval_prompt_version="local-v1",
            eval_prompt_variant="default",
            memory_prompt_identifier="",
            memory_prompt_name="memory-summary",
            memory_prompt_version="local-v1",
            memory_prompt_variant="default",
        ),
        slack_notifier=notifier or LoggingSlackNotifier(),
        slack_signature_service=SlackSignatureService(signing_secret),
        langsmith_tracer=langsmith_tracer,
        pipeline_version="test-v1",
    )


@pytest.fixture
def test_env(monkeypatch, tmp_path: Path):
    database_path = tmp_path / "test.db"
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    monkeypatch.setenv("INTERNAL_API_KEY", "test-internal-key")
    monkeypatch.setenv("ALLOW_DEV_SCHEDULE", "true")
    monkeypatch.setenv("SLACK_SIGNING_SECRET", "dev-slack-secret")

    get_settings.cache_clear()
    get_engine.cache_clear()
    yield
    get_settings.cache_clear()
    get_engine.cache_clear()


@pytest.fixture
def runtime():
    return build_runtime()


@pytest.fixture
def app(test_env, runtime):
    import api.dependencies.auth as auth_module
    from api.dependencies.supabase_store import (
        get_evaluation_store,
        get_job_store,
        get_system_log_store,
        get_user_store,
    )
    from api.dependencies.database import get_session
    from api.dependencies.runtime import get_runtime
    from api.main import create_app

    settings = get_settings()
    connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
    engine = create_engine(settings.database_url, connect_args=connect_args)
    SQLModel.metadata.create_all(engine)

    application = create_app()

    def override_session():
        with Session(engine) as session:
            yield session

    def override_user_store():
        with Session(engine) as session:
            yield FakeUserStore(session)

    def override_evaluation_store():
        with Session(engine) as session:
            yield FakeEvaluationStore(session)

    def override_job_store():
        with Session(engine) as session:
            yield FakeJobStore(session)

    def override_system_log_store():
        with Session(engine) as session:
            yield FakeSystemLogStore(session)

    application.dependency_overrides[get_session] = override_session
    application.dependency_overrides[get_user_store] = override_user_store
    application.dependency_overrides[get_evaluation_store] = override_evaluation_store
    application.dependency_overrides[get_job_store] = override_job_store
    application.dependency_overrides[get_system_log_store] = override_system_log_store
    application.dependency_overrides[get_runtime] = lambda: runtime
    application.state.test_engine = engine
    original_get_token_verifier = auth_module.get_token_verifier
    auth_module.get_token_verifier = lambda: FakeTokenVerifier()

    yield application

    application.dependency_overrides.clear()
    auth_module.get_token_verifier = original_get_token_verifier
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as async_client:
        yield async_client


@pytest.fixture
def db_session(app):
    engine = app.state.test_engine
    with Session(engine) as session:
        yield session


def auth_headers():
    return {
        "Authorization": "Bearer test-supabase-token",
    }


def seed_user(
    session: Session,
    *,
    email: str = "scaffold-user@example.com",
    role: str = "Machine Learning Engineer",
    years_of_experience: int = 6,
) -> User:
    user = User(
        email=email,
        oauth_id=f"dev-oauth:{email}",
        profile_data={
            "role": role,
            "years_of_experience": years_of_experience,
            "title_keywords": ["machine learning", "ml"],
        },
        guidelines={
            "must_haves": ["Python", "SQL", "recommender systems"],
            "deal_breakers": ["contract-only", "pure frontend"],
        },
        notification_settings={"minimum_fit_score": 80, "delivery_channel": "slack"},
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def seed_job_and_evaluation(session: Session, user: User):
    job = Job(
        platform="test_source",
        external_job_id="seed-job",
        title="Senior Machine Learning Engineer",
        company="Signal Labs",
        jd_raw_text="Python SQL recommender systems",
        url="https://example.com/jobs/seed-job",
        min_years_experience=5,
        max_years_experience=8,
        source_metadata={},
    )
    session.add(job)
    session.commit()
    session.refresh(job)

    evaluation = Evaluation(
        user_id=user.id,
        job_id=job.id,
    )
    session.add(evaluation)
    session.commit()
    session.refresh(evaluation)
    return job, evaluation


def sign_slack_body(secret: str, body: bytes, timestamp: str = "1710000000"):
    basestring = f"v0:{timestamp}:{body.decode('utf-8')}"
    digest = hmac.new(secret.encode("utf-8"), basestring.encode("utf-8"), hashlib.sha256).hexdigest()
    return {
        "X-Slack-Request-Timestamp": timestamp,
        "X-Slack-Signature": f"v0={digest}",
    }


def slack_json_payload(evaluation_id: str, feedback: str, feedback_reason: Optional[str] = None) -> bytes:
    payload = {
        "actions": [{"action_id": evaluation_id, "value": feedback}],
    }
    if feedback_reason is not None:
        payload["feedback_reason"] = feedback_reason
    return json.dumps(payload).encode("utf-8")
