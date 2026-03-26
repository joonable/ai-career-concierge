from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from api.dependencies.auth import UserIdentity, get_current_user_identity
from api.dependencies.database import get_session
from api.schemas.users import DashboardResponse, UserProfilePayload, UserProfileResponse
from api.services.dashboard_service import DashboardService
from api.services.profile_service import ProfileService
from db.repositories import EvaluationRepository, UserRepository


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me/profile", response_model=UserProfileResponse)
def get_my_profile(
    identity: UserIdentity = Depends(get_current_user_identity),
    session: Session = Depends(get_session),
) -> UserProfileResponse:
    service = ProfileService(UserRepository(session))
    return service.get_profile(identity)


@router.put("/me/profile", response_model=UserProfileResponse)
def update_my_profile(
    payload: UserProfilePayload,
    identity: UserIdentity = Depends(get_current_user_identity),
    session: Session = Depends(get_session),
) -> UserProfileResponse:
    service = ProfileService(UserRepository(session))
    return service.update_profile(identity, payload)


@router.get("/me/dashboard", response_model=DashboardResponse)
def get_my_dashboard(
    identity: UserIdentity = Depends(get_current_user_identity),
    session: Session = Depends(get_session),
) -> DashboardResponse:
    service = DashboardService(
        user_repository=UserRepository(session),
        evaluation_repository=EvaluationRepository(session),
    )
    return service.get_dashboard(identity)
