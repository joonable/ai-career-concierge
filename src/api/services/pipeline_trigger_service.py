from __future__ import annotations

from typing import List
from uuid import UUID

from agent.nodes.deliver_node import DeliverNode
from agent.nodes.ingest_node import IngestNode
from agent.nodes.llm_eval_node import LLMEvalNode
from agent.nodes.rule_filter_node import RuleFilterNode
from agent.workflow import build_pipeline_graph
from api.schemas.pipeline import PipelineRunResult, PipelineTriggerRequest, PipelineTriggerResponse
from api.services.runtime import RuntimeServices
from common.logging import get_logger
from common.telemetry import start_trace_context
from db.enums import LogLevel

logger = get_logger(__name__)


class NullSlackNotifier:
    async def send_recommendation(self, *, user_context, evaluation_result) -> None:
        del user_context
        del evaluation_result


class PipelineTriggerService:
    def __init__(
        self,
        *,
        user_store,
        job_store,
        evaluation_store,
        system_log_store,
        runtime: RuntimeServices,
    ):
        self.user_store = user_store
        self.job_store = job_store
        self.evaluation_store = evaluation_store
        self.system_log_store = system_log_store
        self.runtime = runtime

    async def trigger(self, payload: PipelineTriggerRequest) -> PipelineTriggerResponse:
        users = self._resolve_users(payload)
        results: List[PipelineRunResult] = []

        for user in users:
            trace_context = start_trace_context()
            recent_memory_prompt = self.runtime.prompt_manager.render_memory_summary(
                self.evaluation_store.list_recent_dislikes(user.user_id, limit=10)
            )
            recent_memory = recent_memory_prompt.text
            user_context = {
                "user_id": str(user.user_id),
                "email": user.email,
                "profile_data": user.profile_data.model_dump(),
                "guidelines": user.guidelines.model_dump(),
                "notification_settings": user.notification_settings.model_dump(exclude_none=True),
                "dashboard_url": "http://localhost:3000/dashboard",
            }

            self.system_log_store.create(
                run_id=trace_context.run_id,
                event_type="pipeline_started",
                level=LogLevel.INFO,
                message="Pipeline run started.",
                user_id=user.user_id,
            )

            with self.runtime.langsmith_tracer.pipeline_run(
                run_id=trace_context.run_id,
                user_id=str(user.user_id),
                dry_run=payload.dry_run,
                app_env=self.runtime.langsmith_tracer.app_env,
            ) as pipeline_trace:
                pipeline_trace.add_metadata(
                    {
                        "pipeline_version": getattr(self.runtime, "pipeline_version", "v1"),
                        "dataset_candidate": False,
                        "user_profile_role": user.profile_data.role,
                        "minimum_fit_score": user.notification_settings.minimum_fit_score,
                        "delivery_channel": user.notification_settings.delivery_channel,
                        "memory_prompt_name": recent_memory_prompt.metadata.prompt_name,
                        "memory_prompt_version": recent_memory_prompt.metadata.prompt_version,
                        "memory_prompt_variant": recent_memory_prompt.metadata.prompt_variant,
                        "memory_prompt_source": recent_memory_prompt.metadata.source,
                        "memory_prompt_identifier": recent_memory_prompt.metadata.prompt_identifier,
                        "memory_requested_prompt_identifier": recent_memory_prompt.metadata.requested_prompt_identifier,
                        "memory_prompt_reference": recent_memory_prompt.metadata.prompt_reference,
                        "memory_prompt_tag": recent_memory_prompt.metadata.prompt_tag,
                        "memory_prompt_commit_hash": recent_memory_prompt.metadata.prompt_commit_hash,
                    }
                )
                graph = build_pipeline_graph(
                    ingest_node=IngestNode(
                        scraper_registry=self.runtime.scraper_registry,
                        job_store=self.job_store,
                        system_log_store=self.system_log_store,
                    ),
                    rule_filter_node=RuleFilterNode(
                        evaluation_store=self.evaluation_store,
                    ),
                    llm_eval_node=LLMEvalNode(
                        evaluator=self.runtime.llm_evaluator,
                        prompt_manager=self.runtime.prompt_manager,
                        tracer=self.runtime.langsmith_tracer,
                        evaluation_store=self.evaluation_store,
                        system_log_store=self.system_log_store,
                    ),
                    deliver_node=DeliverNode(
                        slack_notifier=NullSlackNotifier() if payload.dry_run else self.runtime.slack_notifier
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
                    if result.fit_score >= int(user_context["notification_settings"].get("minimum_fit_score", 80))
                ]
                pipeline_trace.set_outputs(
                    {
                        "run_id": trace_context.run_id,
                        "jobs_ingested": len(final_state.get("current_jobs", [])),
                        "jobs_evaluated": len(final_state.get("evaluation_results", [])),
                        "jobs_sent": 0 if payload.dry_run else len(delivered),
                        "source_errors": final_state.get("source_errors", []),
                    }
                )
                results.append(
                    PipelineRunResult(
                        user_id=user.user_id,
                        run_id=trace_context.run_id,
                        jobs_ingested=len(final_state.get("current_jobs", [])),
                        jobs_sent=0 if payload.dry_run else len(delivered),
                        source_errors=final_state.get("source_errors", []),
                    )
                )
            logger.info(
                "Pipeline run completed.",
                extra={"run_id": trace_context.run_id, "user_id": str(user.user_id)},
            )
        return PipelineTriggerResponse(runs=results)

    def _resolve_users(self, payload: PipelineTriggerRequest):
        if payload.user_id is not None:
            user = self.user_store.get_user_by_id(UUID(str(payload.user_id)))
            if user is None:
                raise ValueError("Requested user_id does not exist.")
            return [user]
        return self.user_store.list_all_users()
