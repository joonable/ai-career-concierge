from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PipelineTriggerRequest(BaseModel):
    user_id: Optional[UUID] = None
    dry_run: bool = False


class PipelineRunResult(BaseModel):
    user_id: UUID
    run_id: str
    jobs_ingested: int
    jobs_sent: int
    source_errors: List[str] = Field(default_factory=list)


class PipelineTriggerResponse(BaseModel):
    runs: List[PipelineRunResult] = Field(default_factory=list)
