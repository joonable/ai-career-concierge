from __future__ import annotations

from fastapi import APIRouter, Depends

from api.dependencies.auth import UserIdentity, get_current_user_identity
from api.dependencies.supabase_store import get_evaluation_store, get_user_store
from api.schemas.users import (
    DashboardResponse,
    PromptOpsDatasetResponse,
    PromptOpsStatusResponse,
    UserProfilePayload,
    UserProfileResponse,
)
from api.services.dashboard_service import DashboardService
from api.services.profile_service import ProfileService
from api.services.promptops_dataset_service import PromptOpsDatasetService
from api.services.promptops_status_service import PromptOpsStatusService

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me/profile", response_model=UserProfileResponse)
def get_my_profile(
    identity: UserIdentity = Depends(get_current_user_identity),
    user_store=Depends(get_user_store),
) -> UserProfileResponse:
    """현재 로그인된 사용자의 프로필 정보(역할, 경력 연차, 설정 등)를 반환합니다."""
    service = ProfileService(user_store)
    return service.get_profile(identity)


@router.put("/me/profile", response_model=UserProfileResponse)
def update_my_profile(
    payload: UserProfilePayload,
    identity: UserIdentity = Depends(get_current_user_identity),
    user_store=Depends(get_user_store),
) -> UserProfileResponse:
    """
    온보딩 단계 및 설정 화면에서 사용자가 입력한 자신의 프로필 세부 요건을 저장합니다.
    여기서 저장한 Deal-breaker나 Must-haves가 파이프라인(LLM 평가)의 기준이 됩니다.
    """
    service = ProfileService(user_store)
    return service.update_profile(identity, payload)


@router.get("/me/dashboard", response_model=DashboardResponse)
def get_my_dashboard(
    identity: UserIdentity = Depends(get_current_user_identity),
    user_store=Depends(get_user_store),
    evaluation_store=Depends(get_evaluation_store),
) -> DashboardResponse:
    """
    Next.js 프론트엔드의 메인 대시보드(칸반 뷰 등)를 그리기 위해,
    평가 상태(Pending, Rule-Rejected, Evaluated 등) 별 추천 공고 목록을 조회 및 가공하여 반환합니다.
    """
    service = DashboardService(
        user_store=user_store,
        evaluation_store=evaluation_store,
    )
    return service.get_dashboard(identity)


@router.get("/me/promptops-status", response_model=PromptOpsStatusResponse)
def get_my_promptops_status(
    identity: UserIdentity = Depends(get_current_user_identity),
) -> PromptOpsStatusResponse:
    service = PromptOpsStatusService()
    return service.get_status(identity)


@router.get("/me/promptops-dataset", response_model=PromptOpsDatasetResponse)
def get_my_promptops_dataset(
    identity: UserIdentity = Depends(get_current_user_identity),
) -> PromptOpsDatasetResponse:
    PromptOpsStatusService().ensure_access(identity)
    return PromptOpsDatasetService().get_dataset()
