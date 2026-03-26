from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.dependencies.auth import UserIdentity, get_current_user_identity
from api.dependencies.database import get_session
from api.schemas.evaluations import FeedbackRequest, FeedbackResponse
from api.services.feedback_service import FeedbackService
from db.repositories import EvaluationRepository, UserRepository


router = APIRouter(prefix="/api/v1/evaluations", tags=["evaluations"])


@router.post("/{evaluation_id}/feedback", response_model=FeedbackResponse)
def record_feedback(
    evaluation_id: UUID,
    payload: FeedbackRequest,
    identity: UserIdentity = Depends(get_current_user_identity),
    session: Session = Depends(get_session),
) -> FeedbackResponse:
    service = FeedbackService(
        session=session,
        user_repository=UserRepository(session),
        evaluation_repository=EvaluationRepository(session),
    )
    return service.record_feedback(
        identity=identity,
        evaluation_id=evaluation_id,
        payload=payload,
    )
