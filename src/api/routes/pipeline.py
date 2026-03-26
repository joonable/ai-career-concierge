from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from api.dependencies.database import get_session
from api.dependencies.internal_api_key import require_internal_api_key
from api.dependencies.runtime import get_runtime
from api.schemas.pipeline import PipelineTriggerRequest, PipelineTriggerResponse
from api.services.pipeline_trigger_service import PipelineTriggerService


router = APIRouter(prefix="/api/v1/pipeline", tags=["pipeline"])


@router.post("/trigger", response_model=PipelineTriggerResponse)
async def trigger_pipeline(
    payload: PipelineTriggerRequest,
    _authorized: None = Depends(require_internal_api_key),
    session: Session = Depends(get_session),
    runtime=Depends(get_runtime),
) -> PipelineTriggerResponse:
    service = PipelineTriggerService(session=session, runtime=runtime)
    try:
        return await service.trigger(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
