from __future__ import annotations

from types import SimpleNamespace

from agent.evals import runner


def test_runner_sync_dataset_command_calls_dataset_helpers(monkeypatch):
    recorded: dict[str, object] = {}

    monkeypatch.setattr(
        "sys.argv",
        [
            "runner.py",
            "sync-dataset",
            "--fixture-path",
            "src/agent/evals/fixtures/job_eval_gold.json",
        ],
    )
    monkeypatch.setattr(
        runner,
        "get_settings",
        lambda: SimpleNamespace(
            langsmith_api_key="test-key",
            langsmith_eval_dataset_name="job-eval-gold-dev",
        ),
    )
    monkeypatch.setattr(runner, "Client", lambda api_key: {"api_key": api_key})
    monkeypatch.setattr(
        runner,
        "load_curated_examples",
        lambda path: [{"id": "11111111-1111-1111-1111-111111111111", "inputs": {}, "outputs": {}}],
    )
    monkeypatch.setattr(
        runner,
        "ensure_dataset",
        lambda client, *, dataset_name, description: recorded.update(
            {"client": client, "dataset_name": dataset_name, "description": description}
        ),
    )
    monkeypatch.setattr(
        runner,
        "sync_examples",
        lambda client, *, dataset_name, examples: recorded.update(
            {"sync_client": client, "sync_dataset_name": dataset_name, "examples": examples}
        ),
    )

    runner.main()

    assert recorded["dataset_name"] == "job-eval-gold-dev"
    assert recorded["sync_dataset_name"] == "job-eval-gold-dev"
    assert recorded["client"] == {"api_key": "test-key"}
    assert len(recorded["examples"]) == 1
