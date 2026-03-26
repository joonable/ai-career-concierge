from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from db.enums import EvaluationStatus, FeedbackState


class UserProfilePayload(BaseModel):
    profile_data: Dict[str, Any] = Field(default_factory=dict)
    guidelines: Dict[str, Any] = Field(default_factory=dict)
    notification_settings: Dict[str, Any] = Field(default_factory=dict)


class UserProfileResponse(UserProfilePayload):
    user_id: UUID
    email: str


class DashboardRecommendation(BaseModel):
    evaluation_id: UUID
    status: EvaluationStatus
    fit_score: Optional[int] = None
    reasoning: Optional[str] = None
    user_feedback: Optional[FeedbackState] = None
    feedback_reason: Optional[str] = None
    job_id: UUID
    title: str
    company: str
    url: str
    platform: str


class DashboardResponse(BaseModel):
    user_id: UUID
    minimum_fit_score: int
    recommendations: List[DashboardRecommendation] = Field(default_factory=list)
