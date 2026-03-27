from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol
from uuid import UUID

from pydantic import ValidationError

from agent.prompts.evaluation_prompt import build_evaluation_prompt
from agent.schemas.evaluation_result import LLMEvaluationResult
from db.enums import LogLevel


class LLMEvaluator(Protocol):
    async def evaluate(
        self,
        *,
        job,
        prompt: str,
        user_context: Dict[str, Any],
        recent_memory: str,
    ) -> Dict[str, Any]:
        ...


@dataclass
class LLMEvalNode:
    evaluator: LLMEvaluator
    evaluation_store: object
    system_log_store: object

    async def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        user_id = UUID(str(state["user_context"]["user_id"]))
        results: List[LLMEvaluationResult] = []

        for job in state.get("current_jobs", []):
            prompt = build_evaluation_prompt(
                user_context=state["user_context"],
                recent_memory=state.get("recent_memory", ""),
                job=job,
            )
            try:
                evaluation = self.evaluation_store.ensure_pending(user_id=user_id, job_id=job.job_id)
                payload = await self.evaluator.evaluate(
                    job=job,
                    prompt=prompt,
                    user_context=state["user_context"],
                    recent_memory=state.get("recent_memory", ""),
                )
                result = LLMEvaluationResult.model_validate(
                    {
                        "evaluation_id": evaluation.id,
                        "job_id": job.job_id,
                        "platform": job.platform,
                        "title": job.title,
                        "company": job.company,
                        "url": job.url,
                        **payload,
                    }
                )
                self.evaluation_store.mark_llm_evaluated(
                    user_id=user_id,
                    job_id=job.job_id,
                    fit_score=result.fit_score,
                    reasoning=result.reasoning,
                )
                results.append(result)
            except (ValidationError, ValueError) as exc:
                self.system_log_store.create(
                    run_id=state["run_id"],
                    event_type="llm_eval_invalid_output",
                    level=LogLevel.ERROR,
                    message=f"LLM evaluation failed for {job.external_job_id}: {exc}",
                    user_id=user_id,
                    job_id=job.job_id,
                    platform=job.platform,
                    metadata={"error_type": exc.__class__.__name__},
                )
            except Exception as exc:  # pragma: no cover - exercised by resilience tests
                self.system_log_store.create(
                    run_id=state["run_id"],
                    event_type="llm_eval_failure",
                    level=LogLevel.ERROR,
                    message=f"LLM evaluation crashed for {job.external_job_id}: {exc}",
                    user_id=user_id,
                    job_id=job.job_id,
                    platform=job.platform,
                    metadata={"error_type": exc.__class__.__name__},
                )

        return {"evaluation_results": results}
