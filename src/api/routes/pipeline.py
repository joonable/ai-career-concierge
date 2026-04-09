from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.internal_api_key import require_internal_api_key
from api.dependencies.runtime import get_runtime
from api.dependencies.supabase_store import (
    get_evaluation_store,
    get_job_store,
    get_system_log_store,
    get_user_store,
)
from api.schemas.pipeline import PipelineTriggerRequest, PipelineTriggerResponse
from api.services.pipeline_trigger_service import PipelineTriggerService

router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])


@router.post("/trigger", response_model=PipelineTriggerResponse)
async def trigger_pipeline(
    payload: PipelineTriggerRequest,
    _authorized: None = Depends(require_internal_api_key),
    user_store=Depends(get_user_store),
    job_store=Depends(get_job_store),
    evaluation_store=Depends(get_evaluation_store),
    system_log_store=Depends(get_system_log_store),
    runtime=Depends(get_runtime),
) -> PipelineTriggerResponse:
    """
    (백그라운드 스케줄러용) 외부 환경(예: GitHub Actions)에서 매일 주기적으로 호출되어
    명시된 사용자의 전체 파이프라인(Scraping -> Filtering -> Eval -> Deliver)을 트리거하는 진입점입니다.
    보안을 위해 내부 API 키(`X-API-Key`) 검증을 요구합니다.
    """
    service = PipelineTriggerService(
        user_store=user_store,
        job_store=job_store,
        evaluation_store=evaluation_store,
        system_log_store=system_log_store,
        runtime=runtime,
    )
    try:
        return await service.trigger(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
