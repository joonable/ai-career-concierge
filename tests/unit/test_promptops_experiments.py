from __future__ import annotations

from types import SimpleNamespace

import pytest

from promptops.adapters.langsmith import LangSmithPromptOpsAdapter
from promptops.core.experiments import run_iteration, sync_dataset
from promptops.core.models import DatasetSyncResult, DatasetSyncSpec, ExperimentRunResult, ExperimentSpec


class FakeIterationAdapter:
    def __init__(self) -> None:
        self.synced = None
        self.ran = None

    def sync_dataset(self, spec):
        self.synced = spec
        return DatasetSyncResult(
            dataset_name=spec.dataset_name,
            dataset_id="dataset-123",
            example_count=15,
            created=2,
            updated=10,
            skipped=3,
        )

    async def run_experiment(self, spec):
        self.ran = spec
        return ExperimentRunResult(
            prompt_family=spec.prompt_family,
            dataset_name=spec.dataset_name,
            experiment_name="structured-eval-local-v3-1234",
            session_id="session-456",
            compare_url="",
            metadata={"backend": "langsmith"},
        )

    def build_compare_link(self, *, dataset_id: str, session_ids: list[str]) -> str:
        return f"https://smith.langchain.com/datasets/{dataset_id}/compare?selectedSessions={session_ids[0]}"


def test_langsmith_adapter_sync_dataset_wraps_dataset_workflow(monkeypatch):
    adapter = LangSmithPromptOpsAdapter(
        client=SimpleNamespace(),
        settings=SimpleNamespace(
            langsmith_api_key="test-key",
            gemini_model="gemini-test",
            langsmith_eval_prompt_identifier="job-evaluation:staging",
            langsmith_eval_prompt_version="local-v3",
        ),
        workspace_id="workspace-123",
    )

    monkeypatch.setattr(
        "promptops.adapters.langsmith.load_curated_examples",
        lambda fixture_path: [{"id": "1", "inputs": {}, "outputs": {}}] * 2,
    )
    monkeypatch.setattr(
        "promptops.adapters.langsmith.ensure_dataset",
        lambda client, *, dataset_name, description: SimpleNamespace(id="dataset-123"),
    )
    monkeypatch.setattr(
        "promptops.adapters.langsmith.sync_examples",
        lambda client, *, dataset_name, examples: {
            "dataset_name": dataset_name,
            "created": 1,
            "updated": 1,
            "skipped": 0,
        },
    )

    result = adapter.sync_dataset(
        DatasetSyncSpec(
            dataset_name="job-eval-gold-dev",
            fixture_path="fixture.json",
            description="Curated gold set",
        )
    )

    assert result.dataset_name == "job-eval-gold-dev"
    assert result.dataset_id == "dataset-123"
    assert result.example_count == 2
    assert result.created == 1
    assert result.updated == 1
    assert result.skipped == 0


def test_langsmith_adapter_build_compare_link_uses_workspace_scope():
    adapter = LangSmithPromptOpsAdapter(
        client=SimpleNamespace(),
        settings=SimpleNamespace(
            langsmith_api_key="test-key",
            gemini_model="gemini-test",
            langsmith_eval_prompt_identifier="job-evaluation:staging",
            langsmith_eval_prompt_version="local-v3",
        ),
        workspace_id="workspace-123",
    )

    compare_link = adapter.build_compare_link(
        dataset_id="dataset-123",
        session_ids=["session-1", "session-2"],
    )

    assert compare_link == (
        "https://smith.langchain.com/o/workspace-123/datasets/dataset-123/compare"
        "?selectedSessions=session-1&selectedSessions=session-2"
    )


@pytest.mark.asyncio
async def test_promptops_iteration_orchestration_runs_sync_and_experiment():
    adapter = FakeIterationAdapter()

    summary = await run_iteration(
        adapter=adapter,
        dataset_spec=DatasetSyncSpec(
            dataset_name="job-eval-gold-dev",
            fixture_path="fixture.json",
            description="Curated gold set",
        ),
        experiment_spec=ExperimentSpec(
            prompt_family="job-evaluation",
            dataset_name="job-eval-gold-dev",
            evaluator_bundle="job-evaluation-v1",
            fixture_path="fixture.json",
            experiment_prefix="structured-eval",
        ),
    )

    assert adapter.synced is not None
    assert adapter.ran is not None
    assert summary.prompt_family == "job-evaluation"
    assert summary.sync_result.updated == 10
    assert summary.experiment_result.session_id == "session-456"
    assert "selectedSessions=session-456" in summary.compare_url
