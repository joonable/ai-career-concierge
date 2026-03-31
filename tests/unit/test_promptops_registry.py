from promptops import ExperimentSpec, IterationRecord, PromptFamily, PromptMetadata, PromptRevision
from promptops.core.registry import get_prompt_family, list_prompt_families, list_prompt_families_by_stage


def test_promptops_models_capture_prompt_lifecycle_metadata():
    family = PromptFamily(
        key="job-evaluation",
        description="test",
        project_key="ai_career_concierge",
        active_stage="candidate",
        metadata=PromptMetadata(
            owner="agent",
            backend="langsmith",
            identifier="job-evaluation",
            local_version="local-v3",
            schema_version=3,
            tags={
                "candidate": "job-evaluation",
                "staging": "job-evaluation:staging",
                "production": "job-evaluation:latest",
            },
        ),
        revisions=[
            PromptRevision(
                family_key="job-evaluation",
                revision_id="local-v3",
                stage="candidate",
                summary="candidate revision",
                change_reason="test",
            )
        ],
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
    assert family.revisions[0].revision_id == "local-v3"
    assert spec.backend == "langsmith"
    assert spec.baseline_revision_id == "local-v2"
    assert record.prompt_revision_id == "local-v3"
    assert record.failure_categories == []


def test_promptops_registry_exposes_registered_prompt_families():
    families = list_prompt_families()

    assert [item.key for item in families] == ["job-evaluation", "memory-summary"]
    assert get_prompt_family("job-evaluation").metadata.local_version == "local-v3"
    assert [item.key for item in list_prompt_families_by_stage("staging")] == [
        "job-evaluation",
        "memory-summary",
    ]
