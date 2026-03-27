from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies.auth import UserIdentity, get_current_user_identity
from api.dependencies.supabase_store import get_evaluation_store, get_user_store
from api.schemas.users import DashboardResponse, UserProfilePayload, UserProfileResponse
from api.services.dashboard_service import DashboardService
from api.services.profile_service import ProfileService


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me/profile", response_model=UserProfileResponse)
def get_my_profile(
    identity: UserIdentity = Depends(get_current_user_identity),
    user_store=Depends(get_user_store),
) -> UserProfileResponse:
    service = ProfileService(user_store)
    return service.get_profile(identity)


@router.put("/me/profile", response_model=UserProfileResponse)
def update_my_profile(
    payload: UserProfilePayload,
    identity: UserIdentity = Depends(get_current_user_identity),
    user_store=Depends(get_user_store),
) -> UserProfileResponse:
    service = ProfileService(user_store)
    return service.update_profile(identity, payload)


@router.get("/me/dashboard", response_model=DashboardResponse)
def get_my_dashboard(
    identity: UserIdentity = Depends(get_current_user_identity),
    user_store=Depends(get_user_store),
    evaluation_store=Depends(get_evaluation_store),
) -> DashboardResponse:
    service = DashboardService(
        user_store=user_store,
        evaluation_store=evaluation_store,
    )
    return service.get_dashboard(identity)
