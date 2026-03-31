from __future__ import annotations

from typing import Any
from uuid import uuid4

from langsmith import Client
from langsmith.evaluation import aevaluate

from agent.evaluation_service import evaluate_job
from agent.evals.dataset_workflow import ensure_dataset, load_curated_examples, sync_examples
from agent.evals.rule_based_evaluators import RULE_BASED_EVALUATORS
from agent.prompts import PromptManager
from agent.schemas.pipeline_job import PipelineJob
from api.services.gemini_evaluator import GeminiEvaluator
from common.config import get_settings
from common.telemetry import LangSmithTracer
from promptops.core.models import (
    DatasetSyncResult,
    DatasetSyncSpec,
    ExperimentRunResult,
    ExperimentSpec,
    ReviewFeedbackRecord,
    ReviewItem,
    ReviewQueueSpec,
)


class LangSmithPromptOpsAdapter:
    """LangSmith-backed PromptOps adapter.

    This adapter wraps the existing evaluation workflow so PromptOps can use
    LangSmith for dataset sync, experiment execution, and compare link creation
    without hard-coding backend details into PromptOps core.
    """

    def __init__(
        self,
        *,
        client: Any | None = None,
        settings: Any | None = None,
        workspace_id: str = "",
        endpoint: str = "https://smith.langchain.com",
    ) -> None:
        self.settings = settings or get_settings()
        self.client = client or Client(api_key=self.settings.langsmith_api_key)
        self.workspace_id = workspace_id
        self.endpoint = endpoint.rstrip("/")

    def sync_dataset(self, spec: DatasetSyncSpec) -> DatasetSyncResult:
        examples = load_curated_examples(spec.fixture_path)
        dataset = ensure_dataset(
            self.client,
            dataset_name=spec.dataset_name,
            description=spec.description,
        )
        result = sync_examples(
            self.client,
            dataset_name=spec.dataset_name,
            examples=examples,
        )
        return DatasetSyncResult(
            dataset_name=spec.dataset_name,
            dataset_id=str(getattr(dataset, "id", "") or ""),
            example_count=len(examples),
            created=int(result.get("created", 0)),
            updated=int(result.get("updated", 0)),
            skipped=int(result.get("skipped", 0)),
        )

    async def run_experiment(self, spec: ExperimentSpec) -> ExperimentRunResult:
        model = spec.model or self.settings.gemini_model
        experiment_name = f"{spec.experiment_prefix}-{self.settings.langsmith_eval_prompt_version}"
        result = await _run_langsmith_experiment(
            client=self.client,
            settings=self.settings,
            dataset_name=spec.dataset_name,
            model=model,
            experiment_prefix=spec.experiment_prefix,
            extra_metadata=spec.metadata,
        )

        compare_url = ""
        session_id = result.get("session_id", "")
        dataset_id = result.get("dataset_id", "")
        if dataset_id and session_id:
            compare_url = self.build_compare_link(
                dataset_id=dataset_id,
                session_ids=[session_id],
            )

        return ExperimentRunResult(
            prompt_family=spec.prompt_family,
            dataset_name=spec.dataset_name,
            experiment_name=result.get("experiment_name") or experiment_name,
            session_id=session_id,
            compare_url=compare_url,
            metadata={
                "backend": "langsmith",
                "model": model,
                "prompt_identifier": self.settings.langsmith_eval_prompt_identifier,
                "prompt_version": self.settings.langsmith_eval_prompt_version,
                **spec.metadata,
            },
        )

    def build_compare_link(self, *, dataset_id: str, session_ids: list[str]) -> str:
        session_params = "&".join(
            f"selectedSessions={session_id}" for session_id in session_ids if session_id
        )
        base = self.endpoint
        if self.workspace_id:
            base = f"{base}/o/{self.workspace_id}"
        if session_params:
            return f"{base}/datasets/{dataset_id}/compare?{session_params}"
        return f"{base}/datasets/{dataset_id}/compare"

    def build_annotation_queue_payload(self, *, queue: ReviewQueueSpec, items: list[ReviewItem]) -> dict[str, Any]:
        """Build a backend-ready annotation queue payload.

        Sprint 5 defines the contract but does not yet create queues remotely.
        """

        return {
            "queue_name": queue.queue_name,
            "description": queue.description,
            "prompt_family": queue.prompt_family,
            "queue_mode": queue.queue_mode,
            "backend": queue.backend,
            "rubric_keys": queue.rubric_keys,
            "items": [
                {
                    "item_id": item.item_id,
                    "experiment_id": item.experiment_id,
                    "run_id": item.run_id,
                    "dataset_example_id": item.dataset_example_id,
                    "status": item.status,
                    "mode": item.mode,
                    "reasons": item.reasons,
                }
                for item in items
            ],
        }

    def build_feedback_payload(self, feedback: ReviewFeedbackRecord) -> dict[str, Any]:
        """Build a backend-ready feedback payload for run or queue attachment."""

        return feedback.model_dump()


async def _run_langsmith_experiment(
    *,
    client: Any,
    settings: Any,
    dataset_name: str,
    model: str,
    experiment_prefix: str,
    extra_metadata: dict[str, str] | None = None,
) -> dict[str, str]:
    tracer = LangSmithTracer.from_settings(settings)
    prompt_manager = PromptManager.from_settings(settings, client=client)
    evaluator = GeminiEvaluator(api_key=settings.gemini_api_key, model=model)

    async def target(inputs):
        job = PipelineJob.model_validate(inputs["job"])
        execution = await evaluate_job(
            evaluator=evaluator,
            prompt_manager=prompt_manager,
            tracer=tracer,
            user_context=inputs["user_context"],
            recent_memory=inputs.get("recent_memory", ""),
            job=job,
            evaluation_id=str(uuid4()),
        )
        payload = execution.result.model_dump()
        payload["prompt_metadata"] = execution.rendered_prompt.metadata.__dict__
        payload["provider_metadata"] = execution.provider_metadata
        return payload

    results = await aevaluate(
        target,
        data=dataset_name,
        evaluators=RULE_BASED_EVALUATORS,
        metadata={
            "prompt_name": settings.langsmith_eval_prompt_name,
            "prompt_identifier": settings.langsmith_eval_prompt_identifier,
            "prompt_version": settings.langsmith_eval_prompt_version,
            "prompt_variant": settings.langsmith_eval_prompt_variant,
            "model": model,
            "dataset_name": dataset_name,
            **(extra_metadata or {}),
        },
        experiment_prefix=f"{experiment_prefix}-{settings.langsmith_eval_prompt_version}",
        description="Offline curated experiment for job evaluation prompt/model comparison.",
        client=client,
        blocking=True,
        max_concurrency=1,
    )
    experiment_name = str(
        getattr(results, "experiment_name", "")
        or getattr(results, "project_name", "")
        or ""
    )
    session_id = _extract_session_id(results)
    dataset_id = _extract_dataset_id(results)
    return {
        "experiment_name": experiment_name,
        "session_id": session_id,
        "dataset_id": dataset_id,
    }


def _extract_session_id(results: Any) -> str:
    experiment_id = getattr(results, "experiment_id", None)
    if experiment_id:
        return str(experiment_id)
    manager = getattr(results, "_manager", None)
    project = getattr(manager, "project", None)
    project_id = getattr(project, "id", None)
    return str(project_id or "")


def _extract_dataset_id(results: Any) -> str:
    manager = getattr(results, "_manager", None)
    dataset_id = getattr(manager, "dataset_id", None)
    if dataset_id:
        return str(dataset_id)
    return ""
