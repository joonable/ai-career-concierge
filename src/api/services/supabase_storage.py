from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import httpx
from fastapi import HTTPException, status

from agent.schemas.pipeline_job import PipelineJob
from api.dependencies.auth import UserIdentity
from api.schemas.users import (
    Guidelines,
    NotificationSettings,
    ProfileData,
    UserProfilePayload,
    UserProfileResponse,
)
from common.config import Settings
from db.enums import EvaluationStatus, FeedbackState, LogLevel
from scraper.base import ScrapedJob


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DashboardRow:
    evaluation_id: UUID
    status: str
    fit_score: Optional[int]
    reasoning: Optional[str]
    user_feedback: Optional[str]
    feedback_reason: Optional[str]
    job_id: UUID
    title: str
    company: str
    url: str
    platform: str


@dataclass
class FeedbackRecord:
    evaluation_id: UUID
    feedback: FeedbackState
    feedback_reason: Optional[str]


@dataclass
class EvaluationRecord:
    id: UUID
    user_id: UUID
    job_id: UUID
    status: EvaluationStatus
    fit_score: Optional[int]
    reasoning: Optional[str]
    rule_rejection_reason: Optional[str]
    user_feedback: Optional[FeedbackState]
    feedback_reason: Optional[str]


@dataclass
class SystemLogRecord:
    id: UUID
    run_id: str
    event_type: str
    level: LogLevel
    message: str
    user_id: Optional[UUID]
    job_id: Optional[UUID]
    platform: Optional[str]
    event_metadata: Dict[str, Any]


class SupabaseRestClient:
    def __init__(self, settings: Settings):
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be configured.")
        self.base_url = f"{settings.supabase_url.rstrip('/')}/rest/v1"
        self.headers = {
            "apikey": settings.supabase_service_role_key,
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "Content-Type": "application/json",
        }

    def select(
        self,
        table: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        response = httpx.get(
            f"{self.base_url}/{table}",
            headers={**self.headers, **(headers or {})},
            params=params,
            timeout=10.0,
        )
        return self._json_response(response)

    def insert(
        self,
        table: str,
        payload: List[Dict[str, Any]],
        *,
        upsert: bool = False,
    ) -> List[Dict[str, Any]]:
        prefer = "return=representation"
        if upsert:
            prefer += ",resolution=merge-duplicates"
        response = httpx.post(
            f"{self.base_url}/{table}",
            headers={**self.headers, "Prefer": prefer},
            json=payload,
            timeout=10.0,
        )
        return self._json_response(response)

    def update(
        self,
        table: str,
        payload: Dict[str, Any],
        *,
        params: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        response = httpx.patch(
            f"{self.base_url}/{table}",
            headers={**self.headers, "Prefer": "return=representation"},
            params=params,
            json=payload,
            timeout=10.0,
        )
        return self._json_response(response)

    @staticmethod
    def _json_response(response: httpx.Response) -> List[Dict[str, Any]]:
        if response.is_success:
            return response.json()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Supabase data API request failed: {response.text}",
        )


class SupabaseUserStore:
    def __init__(self, client: SupabaseRestClient):
        self.client = client

    def upsert_from_identity(self, identity: UserIdentity) -> UserProfileResponse:
        existing = self._find_by_oauth_or_email(identity.oauth_id, identity.email)
        if existing is None:
            payload = {
                "id": str(identity.user_id or uuid4()),
                "oauth_id": identity.oauth_id,
                "email": identity.email,
                "profile_data": {},
                "guidelines": {},
                "notification_settings": {},
                "created_at": utc_now_iso(),
                "updated_at": utc_now_iso(),
            }
            created = self.client.insert("users", [payload])[0]
            return self._to_profile_response(created)

        updates: Dict[str, Any] = {"updated_at": utc_now_iso()}
        if existing.get("oauth_id") != identity.oauth_id:
            updates["oauth_id"] = identity.oauth_id
        if existing.get("email") != identity.email:
            updates["email"] = identity.email

        if len(updates) > 1:
            existing = self.client.update("users", updates, params={"id": f"eq.{existing['id']}"})[0]

        return self._to_profile_response(existing)

    def update_profile(
        self,
        identity: UserIdentity,
        payload: UserProfilePayload,
    ) -> UserProfileResponse:
        user = self.upsert_from_identity(identity)
        updated = self.client.update(
            "users",
            {
                "profile_data": payload.profile_data.model_dump(),
                "guidelines": payload.guidelines.model_dump(),
                "notification_settings": payload.notification_settings.model_dump(exclude_none=True),
                "updated_at": utc_now_iso(),
            },
            params={"id": f"eq.{user.user_id}"},
        )[0]
        return self._to_profile_response(updated)

    def get_user_by_id(self, user_id: UUID) -> Optional[UserProfileResponse]:
        rows = self.client.select(
            "users",
            params={"id": f"eq.{user_id}", "select": "*", "limit": "1"},
        )
        if not rows:
            return None
        return self._to_profile_response(rows[0])

    def list_all_users(self) -> List[UserProfileResponse]:
        rows = self.client.select("users", params={"select": "*"})
        return [self._to_profile_response(row) for row in rows]

    def _find_by_oauth_or_email(self, oauth_id: str, email: str) -> Optional[Dict[str, Any]]:
        by_oauth = self.client.select(
            "users",
            params={"oauth_id": f"eq.{oauth_id}", "select": "*", "limit": "1"},
        )
        if by_oauth:
            return by_oauth[0]

        by_email = self.client.select(
            "users",
            params={"email": f"eq.{email}", "select": "*", "limit": "1"},
        )
        if by_email:
            return by_email[0]

        return None

    def _to_profile_response(self, row: Dict[str, Any]) -> UserProfileResponse:
        profile_data = row.get("profile_data") or {}
        guidelines = row.get("guidelines") or {}
        notification_settings = row.get("notification_settings") or {}

        return UserProfileResponse(
            user_id=UUID(str(row["id"])),
            email=row["email"],
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


class SupabaseEvaluationStore:
    def __init__(self, client: SupabaseRestClient):
        self.client = client

    def list_dashboard_rows(self, user_id: UUID) -> List[DashboardRow]:
        rows = self.client.select(
            "evaluations",
            params={
                "user_id": f"eq.{user_id}",
                "select": (
                    "id,status,fit_score,reasoning,user_feedback,feedback_reason,"
                    "job:jobs!inner(id,title,company,url,platform)"
                ),
                "order": "updated_at.desc",
            },
        )
        payload: List[DashboardRow] = []
        for row in rows:
            job = row["job"]
            payload.append(
                DashboardRow(
                    evaluation_id=UUID(str(row["id"])),
                    status=row["status"],
                    fit_score=row.get("fit_score"),
                    reasoning=row.get("reasoning"),
                    user_feedback=row.get("user_feedback"),
                    feedback_reason=row.get("feedback_reason"),
                    job_id=UUID(str(job["id"])),
                    title=job["title"],
                    company=job["company"],
                    url=job["url"],
                    platform=job["platform"],
                )
            )
        return payload

    def update_feedback(
        self,
        *,
        evaluation_id: UUID,
        feedback: FeedbackState,
        feedback_reason: Optional[str],
        user_id: Optional[UUID] = None,
    ) -> FeedbackRecord:
        params: Dict[str, Any] = {"id": f"eq.{evaluation_id}"}
        if user_id is not None:
            params["user_id"] = f"eq.{user_id}"
        updated = self.client.update(
            "evaluations",
            {
                "user_feedback": feedback.value,
                "feedback_reason": feedback_reason,
                "updated_at": utc_now_iso(),
            },
            params=params,
        )
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found.")
        row = updated[0]
        return FeedbackRecord(
            evaluation_id=UUID(str(row["id"])),
            feedback=FeedbackState(str(row["user_feedback"])),
            feedback_reason=row.get("feedback_reason"),
        )

    def get_by_user_and_job(self, user_id: UUID, job_id: UUID) -> Optional[EvaluationRecord]:
        rows = self.client.select(
            "evaluations",
            params={
                "user_id": f"eq.{user_id}",
                "job_id": f"eq.{job_id}",
                "select": "*",
                "limit": "1",
            },
        )
        if not rows:
            return None
        return self._to_evaluation_record(rows[0])

    def ensure_pending(self, user_id: UUID, job_id: UUID) -> EvaluationRecord:
        existing = self.get_by_user_and_job(user_id, job_id)
        payload = {
            "status": EvaluationStatus.PENDING.value,
            "rule_rejection_reason": None,
            "updated_at": utc_now_iso(),
        }
        if existing is None:
            created = self.client.insert(
                "evaluations",
                [
                    {
                        "id": str(uuid4()),
                        "user_id": str(user_id),
                        "job_id": str(job_id),
                        "status": EvaluationStatus.PENDING.value,
                        "created_at": utc_now_iso(),
                        "updated_at": utc_now_iso(),
                    }
                ],
            )[0]
            return self._to_evaluation_record(created)

        updated = self.client.update(
            "evaluations",
            payload,
            params={"id": f"eq.{existing.id}"},
        )[0]
        return self._to_evaluation_record(updated)

    def mark_rule_rejected(self, user_id: UUID, job_id: UUID, reason: str) -> EvaluationRecord:
        existing = self.get_by_user_and_job(user_id, job_id)
        payload = {
            "status": EvaluationStatus.RULE_REJECTED.value,
            "rule_rejection_reason": reason,
            "fit_score": None,
            "reasoning": None,
            "updated_at": utc_now_iso(),
        }
        if existing is None:
            created = self.client.insert(
                "evaluations",
                [
                    {
                        "id": str(uuid4()),
                        "user_id": str(user_id),
                        "job_id": str(job_id),
                        "status": EvaluationStatus.RULE_REJECTED.value,
                        "rule_rejection_reason": reason,
                        "created_at": utc_now_iso(),
                        "updated_at": utc_now_iso(),
                    }
                ],
            )[0]
            return self._to_evaluation_record(created)

        updated = self.client.update(
            "evaluations",
            payload,
            params={"id": f"eq.{existing.id}"},
        )[0]
        return self._to_evaluation_record(updated)

    def mark_llm_evaluated(
        self,
        user_id: UUID,
        job_id: UUID,
        fit_score: int,
        reasoning: str,
    ) -> EvaluationRecord:
        existing = self.get_by_user_and_job(user_id, job_id)
        payload = {
            "status": EvaluationStatus.LLM_EVALUATED.value,
            "fit_score": fit_score,
            "reasoning": reasoning,
            "rule_rejection_reason": None,
            "updated_at": utc_now_iso(),
        }
        if existing is None:
            created = self.client.insert(
                "evaluations",
                [
                    {
                        "id": str(uuid4()),
                        "user_id": str(user_id),
                        "job_id": str(job_id),
                        "status": EvaluationStatus.LLM_EVALUATED.value,
                        "fit_score": fit_score,
                        "reasoning": reasoning,
                        "created_at": utc_now_iso(),
                        "updated_at": utc_now_iso(),
                    }
                ],
            )[0]
            return self._to_evaluation_record(created)

        updated = self.client.update(
            "evaluations",
            payload,
            params={"id": f"eq.{existing.id}"},
        )[0]
        return self._to_evaluation_record(updated)

    def list_recent_dislikes(self, user_id: UUID, limit: int = 10) -> List[str]:
        rows = self.client.select(
            "evaluations",
            params={
                "user_id": f"eq.{user_id}",
                "user_feedback": f"eq.{FeedbackState.DISLIKE.value}",
                "feedback_reason": "not.is.null",
                "select": "feedback_reason",
                "order": "updated_at.desc",
                "limit": str(limit),
            },
        )
        return [str(row["feedback_reason"]) for row in rows if row.get("feedback_reason")]

    @staticmethod
    def _to_evaluation_record(row: Dict[str, Any]) -> EvaluationRecord:
        user_feedback = row.get("user_feedback")
        return EvaluationRecord(
            id=UUID(str(row["id"])),
            user_id=UUID(str(row["user_id"])),
            job_id=UUID(str(row["job_id"])),
            status=EvaluationStatus(str(row["status"])),
            fit_score=row.get("fit_score"),
            reasoning=row.get("reasoning"),
            rule_rejection_reason=row.get("rule_rejection_reason"),
            user_feedback=FeedbackState(str(user_feedback)) if user_feedback else None,
            feedback_reason=row.get("feedback_reason"),
        )


class SupabaseJobStore:
    def __init__(self, client: SupabaseRestClient):
        self.client = client

    def upsert_job(self, scraped_job: ScrapedJob) -> PipelineJob:
        existing = self.client.select(
            "jobs",
            params={
                "platform": f"eq.{scraped_job.platform}",
                "external_job_id": f"eq.{scraped_job.external_job_id}",
                "select": "*",
                "limit": "1",
            },
        )
        payload = {
            "platform": scraped_job.platform,
            "external_job_id": scraped_job.external_job_id,
            "title": scraped_job.title,
            "company": scraped_job.company,
            "jd_raw_text": scraped_job.jd_raw_text,
            "url": scraped_job.url,
            "min_years_experience": scraped_job.min_years_experience,
            "max_years_experience": scraped_job.max_years_experience,
            "source_metadata": scraped_job.source_metadata,
            "updated_at": utc_now_iso(),
        }
        if not existing:
            row = self.client.insert(
                "jobs",
                [
                    {
                        "id": str(uuid4()),
                        "created_at": utc_now_iso(),
                        **payload,
                    }
                ],
            )[0]
            return self._to_pipeline_job(row)

        row = self.client.update(
            "jobs",
            payload,
            params={"id": f"eq.{existing[0]['id']}"},
        )[0]
        return self._to_pipeline_job(row)

    @staticmethod
    def _to_pipeline_job(row: Dict[str, Any]) -> PipelineJob:
        return PipelineJob(
            job_id=UUID(str(row["id"])),
            platform=row["platform"],
            external_job_id=row["external_job_id"],
            title=row["title"],
            company=row["company"],
            jd_raw_text=row["jd_raw_text"],
            url=row["url"],
            min_years_experience=row.get("min_years_experience"),
            max_years_experience=row.get("max_years_experience"),
            source_metadata=row.get("source_metadata") or {},
        )


class SupabaseSystemLogStore:
    def __init__(self, client: SupabaseRestClient):
        self.client = client

    def create(
        self,
        *,
        run_id: str,
        event_type: str,
        message: str,
        level: LogLevel = LogLevel.INFO,
        user_id: Optional[UUID] = None,
        job_id: Optional[UUID] = None,
        platform: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SystemLogRecord:
        row = self.client.insert(
            "system_logs",
            [
                {
                    "id": str(uuid4()),
                    "run_id": run_id,
                    "event_type": event_type,
                    "level": level.value,
                    "message": message,
                    "user_id": str(user_id) if user_id else None,
                    "job_id": str(job_id) if job_id else None,
                    "platform": platform,
                    "metadata": metadata or {},
                    "created_at": utc_now_iso(),
                }
            ],
        )[0]
        return SystemLogRecord(
            id=UUID(str(row["id"])),
            run_id=row["run_id"],
            event_type=row["event_type"],
            level=LogLevel(str(row["level"])),
            message=row["message"],
            user_id=UUID(str(row["user_id"])) if row.get("user_id") else None,
            job_id=UUID(str(row["job_id"])) if row.get("job_id") else None,
            platform=row.get("platform"),
            event_metadata=row.get("metadata") or {},
        )
