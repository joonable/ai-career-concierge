from __future__ import annotations

from promptops.core.models import (
    DatasetSyncResult,
    DatasetSyncSpec,
    ExperimentRunResult,
    ExperimentSpec,
    IterationSummary,
)


def sync_dataset(*, adapter, spec: DatasetSyncSpec) -> DatasetSyncResult:
    """Sync a curated dataset through the configured backend adapter."""

    return adapter.sync_dataset(spec)


async def run_experiment(*, adapter, spec: ExperimentSpec) -> ExperimentRunResult:
    """Run a PromptOps experiment through the configured backend adapter."""

    return await adapter.run_experiment(spec)


async def run_iteration(*, adapter, dataset_spec: DatasetSyncSpec, experiment_spec: ExperimentSpec) -> IterationSummary:
    """Execute dataset sync + experiment run as one PromptOps iteration unit."""

    sync_result = sync_dataset(adapter=adapter, spec=dataset_spec)
    experiment_result = await run_experiment(adapter=adapter, spec=experiment_spec)
    compare_url = experiment_result.compare_url
    if not compare_url and sync_result.dataset_id and experiment_result.session_id:
        compare_url = adapter.build_compare_link(
            dataset_id=sync_result.dataset_id,
            session_ids=[experiment_result.session_id],
        )

    return IterationSummary(
        prompt_family=experiment_spec.prompt_family,
        dataset_name=dataset_spec.dataset_name,
        sync_result=sync_result,
        experiment_result=experiment_result,
        compare_url=compare_url,
    )
