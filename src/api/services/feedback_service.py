from __future__ import annotations

import json
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import Session

from api.dependencies.auth import UserIdentity
from api.schemas.evaluations import FeedbackRequest, FeedbackResponse
from db.enums import FeedbackState
from db.models import Evaluation
from db.repositories import EvaluationRepository, UserRepository


class FeedbackService:
    def __init__(
        self,
        session: Session,
        user_repository: UserRepository,
        evaluation_repository: EvaluationRepository,
    ):
        self.session = session
        self.user_repository = user_repository
        self.evaluation_repository = evaluation_repository

    def record_feedback(
        self,
        *,
        identity: UserIdentity,
        evaluation_id: UUID,
        payload: FeedbackRequest,
    ) -> FeedbackResponse:
        user = self.user_repository.upsert_from_identity(
            email=identity.email,
            oauth_id=identity.oauth_id,
            preferred_user_id=identity.user_id,
        )
        evaluation = self.session.get(Evaluation, evaluation_id)
        if evaluation is None or evaluation.user_id != user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found.")

        updated = self.evaluation_repository.update_feedback(
            evaluation_id=evaluation_id,
            feedback=payload.feedback,
            feedback_reason=payload.feedback_reason,
        )
        return FeedbackResponse(
            evaluation_id=updated.id,
            feedback=updated.user_feedback,
            feedback_reason=updated.feedback_reason,
        )

    def record_feedback_from_slack(self, payload: Dict[str, Any]) -> FeedbackResponse:
        actions = payload.get("actions", [])
        if not actions:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Slack action.")

        action = actions[0]
        feedback_value = action.get("value")
        evaluation_id = action.get("action_id")
        feedback_reason = payload.get("feedback_reason")
        if evaluation_id is None or feedback_value is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slack payload is incomplete.")

        updated = self.evaluation_repository.update_feedback(
            evaluation_id=UUID(str(evaluation_id)),
            feedback=FeedbackState(feedback_value),
            feedback_reason=feedback_reason,
        )
        return FeedbackResponse(
            evaluation_id=updated.id,
            feedback=updated.user_feedback,
            feedback_reason=updated.feedback_reason,
        )

    @staticmethod
    def parse_slack_payload(raw_payload: str) -> Dict[str, Any]:
        return json.loads(raw_payload)
