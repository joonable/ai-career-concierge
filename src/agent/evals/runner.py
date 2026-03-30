from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
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


DEFAULT_FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "job_eval_gold.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="LangSmith offline eval workflow for job evaluation.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sync_parser = subparsers.add_parser("sync-dataset", help="Create or update the curated LangSmith dataset.")
    sync_parser.add_argument("--dataset-name", default=None)
    sync_parser.add_argument("--fixture-path", default=str(DEFAULT_FIXTURE_PATH))

    run_parser = subparsers.add_parser("run-experiment", help="Run an offline experiment against a LangSmith dataset.")
    run_parser.add_argument("--dataset-name", default=None)
    run_parser.add_argument("--fixture-path", default=str(DEFAULT_FIXTURE_PATH))
    run_parser.add_argument("--model", default=None)
    run_parser.add_argument("--experiment-prefix", default="eval-prompt")

    promote_parser = subparsers.add_parser("promote-trace", help="Create a dataset-ready candidate from a production trace.")
    promote_parser.add_argument("--run-id", required=True)
    promote_parser.add_argument("--dataset-name", default=None)
    promote_parser.add_argument("--approve", action="store_true")

    args = parser.parse_args()
    settings = get_settings()
    client = Client(api_key=settings.langsmith_api_key)

    if args.command == "sync-dataset":
        dataset_name = args.dataset_name or settings.langsmith_eval_dataset_name
        examples = load_curated_examples(args.fixture_path)
        ensure_dataset(client, dataset_name=dataset_name, description="Curated gold set for job evaluation experiments.")
        sync_examples(client, dataset_name=dataset_name, examples=examples)
        print(json.dumps({"dataset_name": dataset_name, "example_count": len(examples)}, indent=2))
        return

    if args.command == "run-experiment":
        dataset_name = args.dataset_name or settings.langsmith_eval_dataset_name
        examples = load_curated_examples(args.fixture_path)
        ensure_dataset(client, dataset_name=dataset_name, description="Curated gold set for job evaluation experiments.")
        sync_examples(client, dataset_name=dataset_name, examples=examples)
        asyncio.run(
            _run_experiment(
                client=client,
                dataset_name=dataset_name,
                model=args.model or settings.gemini_model,
                experiment_prefix=args.experiment_prefix,
            )
        )
        return

    if args.command == "promote-trace":
        dataset_name = args.dataset_name or settings.langsmith_eval_dataset_name
        asyncio.run(
            _promote_trace(
                client=client,
                run_id=args.run_id,
                dataset_name=dataset_name,
                approve=args.approve,
            )
        )


async def _run_experiment(*, client, dataset_name: str, model: str, experiment_prefix: str) -> None:
    settings = get_settings()
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
            "prompt_version": settings.langsmith_eval_prompt_version,
            "prompt_variant": settings.langsmith_eval_prompt_variant,
            "model": model,
            "dataset_name": dataset_name,
        },
        experiment_prefix=f"{experiment_prefix}-{settings.langsmith_eval_prompt_version}",
        description="Offline curated experiment for job evaluation prompt/model comparison.",
        client=client,
        blocking=True,
        max_concurrency=1,
    )
    print(results)


async def _promote_trace(*, client, run_id: str, dataset_name: str, approve: bool) -> None:
    run = client.read_run(run_id, load_child_runs=True)
    candidate = {
        "inputs": run.inputs or {},
        "outputs": run.outputs or {},
        "metadata": {
            "source": "trace-review",
            "trace_id": str(run.trace_id),
            "run_id": str(run.id),
            "prompt_name": ((run.extra or {}).get("metadata") or {}).get("prompt_name"),
            "prompt_version": ((run.extra or {}).get("metadata") or {}).get("prompt_version"),
        },
    }
    if not approve:
        print(json.dumps(candidate, indent=2, default=str))
        return

    ensure_dataset(client, dataset_name=dataset_name, description="Curated gold set for job evaluation experiments.")
    sync_examples(
        client,
        dataset_name=dataset_name,
        examples=[{"id": str(uuid4()), **candidate}],
    )
    print(json.dumps({"dataset_name": dataset_name, "promoted_run_id": run_id}, indent=2))
