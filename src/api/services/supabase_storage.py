from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

import httpx
from fastapi import HTTPException, status

from api.dependencies.auth import UserIdentity
from api.schemas.users import (
    Guidelines,
    NotificationSettings,
    ProfileData,
    UserProfilePayload,
    UserProfileResponse,
)
from common.config import Settings
from db.enums import FeedbackState


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

    def list_all_ids(self) -> List[UUID]:
        rows = self.client.select("users", params={"select": "id"})
        return [UUID(str(row["id"])) for row in rows]

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
