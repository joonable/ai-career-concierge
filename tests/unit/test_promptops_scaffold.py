from promptops import ExperimentSpec, IterationRecord, PromptFamily
from promptops.projects.ai_career_concierge.prompts import PROMPT_FAMILIES


def test_promptops_scaffold_imports_and_prompt_family_bindings():
    family = PromptFamily(
        key="job-evaluation",
        description="test",
        project_key="ai_career_concierge",
        active_stage="candidate",
    )
    spec = ExperimentSpec(
        prompt_family="job-evaluation",
        dataset_name="job-eval-gold-dev",
        evaluator_bundle="job-evaluation-v1",
    )
    record = IterationRecord(
        prompt_family="job-evaluation",
        goal="Reduce adjacent-role band drift.",
    )

    assert family.key == "job-evaluation"
    assert spec.backend == "langsmith"
    assert record.failure_categories == []
    assert [item.key for item in PROMPT_FAMILIES] == ["job-evaluation", "memory-summary"]
