from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from api.dependencies.auth import UserIdentity, get_current_user_identity
from api.dependencies.supabase_store import get_evaluation_store, get_user_store
from api.schemas.evaluations import FeedbackRequest, FeedbackResponse
from api.services.feedback_service import FeedbackService

router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


@router.post("/{evaluation_id}/feedback", response_model=FeedbackResponse)
def record_feedback(
    evaluation_id: UUID,
    payload: FeedbackRequest,
    identity: UserIdentity = Depends(get_current_user_identity),
    user_store=Depends(get_user_store),
    evaluation_store=Depends(get_evaluation_store),
) -> FeedbackResponse:
    service = FeedbackService(
        user_store=user_store,
        evaluation_store=evaluation_store,
    )
    return service.record_feedback(
        identity=identity,
        evaluation_id=evaluation_id,
        payload=payload,
    )
