from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List
from uuid import UUID

from pydantic import ValidationError

from agent.evaluation_service import evaluate_job
from agent.prompts.prompt_manager import PromptManager
from agent.schemas.evaluation_result import LLMEvaluationResult
from common.errors import PromptLoadError, ProviderRequestError, ProviderResponseParseError
from common.logging import get_logger
from db.enums import LogLevel


logger = get_logger(__name__)


@dataclass
class LLMEvalNode:
    evaluator: LLMEvaluator
    prompt_manager: PromptManager
    tracer: object
    evaluation_store: object
    system_log_store: object

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_id = UUID(str(state["user_context"]["user_id"]))
        results: List[LLMEvaluationResult] = []

        for job in state.get("current_jobs", []):
            try:
                evaluation = self.evaluation_store.ensure_pending(user_id=user_id, job_id=job.job_id)
                execution = await evaluate_job(
                    evaluator=self.evaluator,
                    prompt_manager=self.prompt_manager,
                    tracer=self.tracer,
                    user_context=state["user_context"],
                    recent_memory=state.get("recent_memory", ""),
                    job=job,
                    evaluation_id=str(evaluation.id),
                )
                result = execution.result
                self.evaluation_store.mark_llm_evaluated(
                    user_id=user_id,
                    job_id=job.job_id,
                    fit_score=result.fit_score,
                    reasoning=result.reasoning,
                )
                logger.info(
                    "LLM evaluation completed.",
                    extra={
                        "run_id": state["run_id"],
                        "user_id": str(user_id),
                        "job_id": str(job.job_id),
                        "platform": job.platform,
                        "model": execution.provider_metadata.get("model"),
                        "latency_ms": execution.provider_metadata.get("latency_ms"),
                    },
                )
                results.append(result)
            except (ValidationError, ProviderResponseParseError) as exc:
                self._record_failure(
                    state=state,
                    user_id=user_id,
                    job=job,
                    exc=exc,
                    event_type="llm_eval_invalid_output",
                    failure_stage="schema_validate" if isinstance(exc, ValidationError) else "json_parse",
                )
            except PromptLoadError as exc:
                self._record_failure(
                    state=state,
                    user_id=user_id,
                    job=job,
                    exc=exc,
                    event_type="llm_eval_failure",
                    failure_stage="prompt_load",
                )
            except ProviderRequestError as exc:
                self._record_failure(
                    state=state,
                    user_id=user_id,
                    job=job,
                    exc=exc,
                    event_type="llm_eval_failure",
                    failure_stage="provider_request",
                )
            except Exception as exc:  # pragma: no cover - exercised by resilience tests
                self._record_failure(
                    state=state,
                    user_id=user_id,
                    job=job,
                    exc=exc,
                    event_type="llm_eval_failure",
                    failure_stage="unknown",
                )

        return {"evaluation_results": results}

    def _record_failure(self, *, state: Dict[str, Any], user_id: UUID, job, exc: Exception, event_type: str, failure_stage: str) -> None:
        self.system_log_store.create(
            run_id=state["run_id"],
            event_type=event_type,
            level=LogLevel.ERROR,
            message=f"LLM evaluation failed for {job.external_job_id}: {exc}",
            user_id=user_id,
            job_id=job.job_id,
            platform=job.platform,
            metadata={"error_type": exc.__class__.__name__, "failure_stage": failure_stage},
        )
