from __future__ import annotations

import json
from typing import Any, Dict
from uuid import UUID

from fastapi import HTTPException, status

from api.dependencies.auth import UserIdentity
from api.schemas.evaluations import FeedbackRequest, FeedbackResponse
from db.enums import FeedbackState


class FeedbackService:
    def __init__(
        self,
        user_store,
        evaluation_store,
    ):
        self.user_store = user_store
        self.evaluation_store = evaluation_store

    def record_feedback(
        self,
        *,
        identity: UserIdentity,
        evaluation_id: UUID,
        payload: FeedbackRequest,
    ) -> FeedbackResponse:
        user = self.user_store.upsert_from_identity(identity)
        updated = self.evaluation_store.update_feedback(
            evaluation_id=evaluation_id,
            feedback=payload.feedback,
            feedback_reason=payload.feedback_reason,
            user_id=user.user_id,
        )
        return FeedbackResponse(
            evaluation_id=updated.evaluation_id,
            feedback=updated.feedback,
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

        updated = self.evaluation_store.update_feedback(
            evaluation_id=UUID(str(evaluation_id)),
            feedback=FeedbackState(feedback_value),
            feedback_reason=feedback_reason,
        )
        return FeedbackResponse(
            evaluation_id=updated.evaluation_id,
            feedback=updated.feedback,
            feedback_reason=updated.feedback_reason,
        )

    @staticmethod
    def parse_slack_payload(raw_payload: str) -> Dict[str, Any]:
        return json.loads(raw_payload)
