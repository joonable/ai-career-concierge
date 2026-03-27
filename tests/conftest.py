from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path
from typing import Iterable, List, Optional

import pytest
from httpx import ASGITransport, AsyncClient
from sqlmodel import Session, SQLModel, create_engine

from api.services.mock_llm_evaluator import MockGeminiEvaluator
from api.services.runtime import RuntimeServices
from api.services.slack_notifier import LoggingSlackNotifier
from api.services.slack_signature_service import SlackSignatureService
from api.services.supabase_storage import DashboardRow, FeedbackRecord
from common.config import get_settings
from db.enums import FeedbackState
from db.models import Evaluation, Job, User
from db.repositories import EvaluationRepository, UserRepository
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
    async def evaluate(self, *, job, prompt, user_context, recent_memory):
        del job
        del prompt
        del user_context
        del recent_memory
        return {
            "fit_score": 999,
            "reasoning": "invalid output",
            "must_have_hits": [],
            "deal_breakers_found": [],
        }


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


class TestUserStore:
    def __init__(self, session: Session):
        self.repo = UserRepository(session)

    def upsert_from_identity(self, identity):
        from api.schemas.users import Guidelines, NotificationSettings, ProfileData, UserProfileResponse

        user = self.repo.upsert_from_identity(
            email=identity.email,
            oauth_id=identity.oauth_id,
            preferred_user_id=identity.user_id,
        )
        profile_data = user.profile_data or {}
        guidelines = user.guidelines or {}
        notification_settings = user.notification_settings or {}
        return UserProfileResponse(
            user_id=user.id,
            email=user.email,
            profile_data=ProfileData.model_construct(
                role=str(profile_data.get("role", "")),
                years_of_experience=int(profile_data.get("years_of_experience", 0)),
                title_keywords=list(profile_data.get("title_keywords", [])),
            ),
            guidelines=Guidelines.model_construct(
                must_haves=list(guidelines.get("must_haves", [])),
                deal_breakers=list(guidelines.get("deal_breakers", [])),
            ),
            notification_settings=NotificationSettings.model_construct(
                minimum_fit_score=int(notification_settings.get("minimum_fit_score", 80)),
                delivery_channel=notification_settings.get("delivery_channel"),
            ),
        )

    def update_profile(self, identity, payload):
        user = self.repo.upsert_from_identity(
            email=identity.email,
            oauth_id=identity.oauth_id,
            preferred_user_id=identity.user_id,
        )
        updated = self.repo.update_profile(
            user=user,
            profile_data=payload.profile_data.model_dump(),
            guidelines=payload.guidelines.model_dump(),
            notification_settings=payload.notification_settings.model_dump(exclude_none=True),
        )
        identity.user_id = updated.id
        return self.upsert_from_identity(identity)


class TestEvaluationStore:
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
                user_feedback=(
                    evaluation.user_feedback.value
                    if getattr(evaluation.user_feedback, "value", None)
                    else evaluation.user_feedback
                ),
                feedback_reason=evaluation.feedback_reason,
                job_id=job.id,
                title=job.title,
                company=job.company,
                url=job.url,
                platform=job.platform,
            )
            for evaluation, job in rows
        ]

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


def build_runtime(
    *,
    scrapers: Optional[Iterable[object]] = None,
    evaluator: Optional[object] = None,
    notifier: Optional[LoggingSlackNotifier] = None,
    signing_secret: str = "dev-slack-secret",
) -> RuntimeServices:
    return RuntimeServices(
        scraper_registry=ScraperRegistry(scrapers or [StaticScraper()]),
        llm_evaluator=evaluator or MockGeminiEvaluator(),
        slack_notifier=notifier or LoggingSlackNotifier(),
        slack_signature_service=SlackSignatureService(signing_secret),
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
    from api.dependencies.supabase_store import get_evaluation_store, get_user_store
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
            yield TestUserStore(session)

    def override_evaluation_store():
        with Session(engine) as session:
            yield TestEvaluationStore(session)

    application.dependency_overrides[get_session] = override_session
    application.dependency_overrides[get_user_store] = override_user_store
    application.dependency_overrides[get_evaluation_store] = override_evaluation_store
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
        notification_settings={"minimum_fit_score": 80},
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
