from promptops import ExperimentSpec, IterationRecord, PromptFamily, PromptMetadata
from promptops.core.registry import get_prompt_family, list_prompt_families


def test_promptops_models_capture_runtime_prompt_binding():
    family = PromptFamily(
        key="job-evaluation",
        description="test",
        project_key="ai_career_concierge",
        metadata=PromptMetadata(
            owner="agent",
            backend="langsmith",
            identifier="job-evaluation",
            schema_version=3,
            tags={
                "candidate": "job-evaluation",
                "staging": "job-evaluation:staging",
                "production": "job-evaluation:latest",
            },
        ),
    )
    spec = ExperimentSpec(
        prompt_family="job-evaluation",
        dataset_name="job-eval-gold-dev",
        evaluator_bundle="job-evaluation-v1",
        baseline_revision_id="local-v2",
        candidate_revision_id="local-v3",
    )
    record = IterationRecord(
        prompt_family="job-evaluation",
        goal="Reduce adjacent-role band drift.",
        stage="candidate",
        prompt_revision_id="local-v3",
    )

    assert family.metadata.identifier == "job-evaluation"
    assert family.metadata.schema_version == 3
    assert family.metadata.tags["production"] == "job-evaluation:latest"
    assert spec.backend == "langsmith"
    assert spec.baseline_revision_id == "local-v2"
    assert record.prompt_revision_id == "local-v3"
    assert record.failure_categories == []


def test_promptops_registry_exposes_prompt_family_bindings():
    families = list_prompt_families()

    assert [item.key for item in families] == ["job-evaluation", "memory-summary"]
    assert get_prompt_family("job-evaluation").metadata.identifier == "job-evaluation"
    assert get_prompt_family("job-evaluation").metadata.schema_version == 3
    assert get_prompt_family("job-evaluation").metadata.tags == {
        "candidate": "job-evaluation",
        "staging": "job-evaluation:staging",
        "production": "job-evaluation:latest",
    }
