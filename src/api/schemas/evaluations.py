from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from db.enums import FeedbackState


class FeedbackRequest(BaseModel):
    feedback: FeedbackState
    feedback_reason: Optional[str] = None


class FeedbackResponse(BaseModel):
    evaluation_id: UUID
    feedback: FeedbackState
    feedback_reason: Optional[str] = None
