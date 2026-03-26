from __future__ import annotations

from typing import Any, Dict, List, TypedDict

from agent.schemas.evaluation_result import LLMEvaluationResult
from agent.schemas.pipeline_job import PipelineJob


class AgentState(TypedDict, total=False):
    current_jobs: List[PipelineJob]
    user_context: Dict[str, Any]
    recent_memory: str
    evaluation_results: List[LLMEvaluationResult]
    run_id: str
    source_errors: List[str]
