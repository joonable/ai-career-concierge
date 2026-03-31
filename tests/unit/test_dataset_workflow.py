from __future__ import annotations

from types import SimpleNamespace

from agent.evals.dataset_workflow import sync_examples


class FakeClient:
    def __init__(self, existing_examples):
        self._existing_examples = existing_examples
        self.created_examples = []
        self.updated_examples = []

    def list_examples(self, *, dataset_name: str, limit: int):
        assert dataset_name == "job-eval-gold-dev"
        assert limit == 500
        return list(self._existing_examples)

    def create_examples(self, *, dataset_name: str, examples):
        assert dataset_name == "job-eval-gold-dev"
        self.created_examples.extend(examples)
        return {"created": len(examples)}

    def update_example(self, example_id, *, inputs, outputs, metadata, split):
        self.updated_examples.append(
            {
                "id": str(example_id),
                "inputs": inputs,
                "outputs": outputs,
                "metadata": metadata,
                "split": split,
            }
        )
        return {"id": str(example_id)}


def test_sync_examples_updates_existing_example_when_payload_changes():
    client = FakeClient(
        [
            SimpleNamespace(
                id="11111111-1111-1111-1111-111111111111",
                inputs={"job": {"title": "Old title"}},
                outputs={"fit_score_range": {"min": 40, "max": 59}},
                metadata={"scenario_type": "borderline_case", "scenario_family": "analytics_infra"},
                split=["gold", "borderline_case"],
            )
        ]
    )

    examples = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "inputs": {"job": {"title": "New title"}},
            "outputs": {"fit_score_range": {"min": 40, "max": 59}, "scoring_note": "updated"},
            "metadata": {"scenario_type": "borderline_case", "scenario_family": "analytics_infra"},
        }
    ]

    result = sync_examples(client, dataset_name="job-eval-gold-dev", examples=examples)

    assert result == {
        "dataset_name": "job-eval-gold-dev",
        "created": 0,
        "updated": 1,
        "skipped": 0,
    }
    assert client.created_examples == []
    assert client.updated_examples == [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "inputs": {"job": {"title": "New title"}},
            "outputs": {"fit_score_range": {"min": 40, "max": 59}, "scoring_note": "updated"},
            "metadata": {"scenario_type": "borderline_case", "scenario_family": "analytics_infra"},
            "split": ["gold", "borderline_case"],
        }
    ]


def test_sync_examples_skips_existing_example_when_payload_matches():
    client = FakeClient(
        [
            SimpleNamespace(
                id="11111111-1111-1111-1111-111111111111",
                inputs={"job": {"title": "Same title"}},
                outputs={"fit_score_range": {"min": 40, "max": 59}, "scoring_note": "same"},
                metadata={"scenario_type": "borderline_case", "scenario_family": "analytics_infra"},
                split=["gold", "borderline_case"],
            )
        ]
    )

    examples = [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "inputs": {"job": {"title": "Same title"}},
            "outputs": {"fit_score_range": {"min": 40, "max": 59}, "scoring_note": "same"},
            "metadata": {"scenario_type": "borderline_case", "scenario_family": "analytics_infra"},
        }
    ]

    result = sync_examples(client, dataset_name="job-eval-gold-dev", examples=examples)

    assert result == {
        "dataset_name": "job-eval-gold-dev",
        "created": 0,
        "updated": 0,
        "skipped": 1,
    }
    assert client.created_examples == []
    assert client.updated_examples == []


def test_sync_examples_creates_missing_examples():
    client = FakeClient([])

    examples = [
        {
            "id": "22222222-2222-2222-2222-222222222222",
            "inputs": {"job": {"title": "New example"}},
            "outputs": {"fit_score_range": {"min": 60, "max": 79}, "scoring_note": "new"},
            "metadata": {"scenario_type": "adjacent_role", "scenario_family": "ml_adjacent_data_engineer"},
        }
    ]

    result = sync_examples(client, dataset_name="job-eval-gold-dev", examples=examples)

    assert result == {
        "dataset_name": "job-eval-gold-dev",
        "created": 1,
        "updated": 0,
        "skipped": 0,
    }
    assert len(client.created_examples) == 1
    created = client.created_examples[0]
    assert str(created.id) == "22222222-2222-2222-2222-222222222222"
    assert created.inputs == {"job": {"title": "New example"}}
    assert created.outputs == {"fit_score_range": {"min": 60, "max": 79}, "scoring_note": "new"}
    assert created.metadata == {
        "scenario_type": "adjacent_role",
        "scenario_family": "ml_adjacent_data_engineer",
    }
    assert created.split == ["gold", "adjacent_role"]
    assert client.updated_examples == []
