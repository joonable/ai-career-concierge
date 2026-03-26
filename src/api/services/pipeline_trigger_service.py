from __future__ import annotations

from typing import List
from uuid import UUID

from agent.nodes.deliver_node import DeliverNode
from agent.nodes.ingest_node import IngestNode
from agent.nodes.llm_eval_node import LLMEvalNode
from agent.nodes.rule_filter_node import RuleFilterNode
from agent.prompts.memory_summary import summarize_recent_dislikes
from agent.workflow import build_pipeline_graph
from api.schemas.pipeline import PipelineRunResult, PipelineTriggerRequest, PipelineTriggerResponse
from api.services.runtime import RuntimeServices
from common.logging import get_logger
from common.telemetry import start_trace_context
from db.enums import LogLevel
from db.repositories import EvaluationRepository, JobRepository, SystemLogRepository, UserRepository


logger = get_logger(__name__)


class NullSlackNotifier:
    async def send_recommendation(self, *, user_context, evaluation_result) -> None:
        del user_context
        del evaluation_result


class PipelineTriggerService:
    def __init__(self, session, runtime: RuntimeServices):
        self.user_repository = UserRepository(session)
        self.job_repository = JobRepository(session)
        self.evaluation_repository = EvaluationRepository(session)
        self.system_log_repository = SystemLogRepository(session)
        self.runtime = runtime

    async def trigger(self, payload: PipelineTriggerRequest) -> PipelineTriggerResponse:
        users = self._resolve_users(payload)
        results: List[PipelineRunResult] = []

        for user in users:
            trace_context = start_trace_context()
            recent_memory = summarize_recent_dislikes(
                self.evaluation_repository.list_recent_dislikes(user.id, limit=10)
            )
            user_context = {
                "user_id": str(user.id),
                "email": user.email,
                "profile_data": user.profile_data,
                "guidelines": user.guidelines,
                "notification_settings": user.notification_settings or {"minimum_fit_score": 80},
                "dashboard_url": "http://localhost:3000/dashboard",
            }

            self.system_log_repository.create(
                run_id=trace_context.run_id,
                event_type="pipeline_started",
                level=LogLevel.INFO,
                message="Pipeline run started.",
                user_id=user.id,
            )

            graph = build_pipeline_graph(
                ingest_node=IngestNode(
                    scraper_registry=self.runtime.scraper_registry,
                    job_repository=self.job_repository,
                    system_log_repository=self.system_log_repository,
                ),
                rule_filter_node=RuleFilterNode(
                    evaluation_repository=self.evaluation_repository,
                ),
                llm_eval_node=LLMEvalNode(
                    evaluator=self.runtime.llm_evaluator,
                    evaluation_repository=self.evaluation_repository,
                    system_log_repository=self.system_log_repository,
                ),
                deliver_node=DeliverNode(
                    slack_notifier=NullSlackNotifier()
                    if payload.dry_run
                    else self.runtime.slack_notifier
                ),
            )

            final_state = await graph.ainvoke(
                {
                    "current_jobs": [],
                    "user_context": user_context,
                    "recent_memory": recent_memory,
                    "evaluation_results": [],
                    "run_id": trace_context.run_id,
                    "source_errors": [],
                }
            )

            delivered = [
                result
                for result in final_state.get("evaluation_results", [])
                if result.fit_score
                >= int(user_context["notification_settings"].get("minimum_fit_score", 80))
            ]
            results.append(
                PipelineRunResult(
                    user_id=user.id,
                    run_id=trace_context.run_id,
                    jobs_ingested=len(final_state.get("current_jobs", [])),
                    jobs_sent=0 if payload.dry_run else len(delivered),
                    source_errors=final_state.get("source_errors", []),
                )
            )
            logger.info(
                "Pipeline run completed.",
                extra={"run_id": trace_context.run_id, "user_id": str(user.id)},
            )
        return PipelineTriggerResponse(runs=results)

    def _resolve_users(self, payload: PipelineTriggerRequest):
        if payload.user_id is not None:
            user = self.user_repository.get_by_id(UUID(str(payload.user_id)))
            if user is None:
                raise ValueError("Requested user_id does not exist.")
            return [user]
        return self.user_repository.list_all()
