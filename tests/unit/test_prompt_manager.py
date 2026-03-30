from pathlib import Path

from agent.evals.dataset_workflow import load_curated_examples
from agent.evals.rule_based_evaluators import (
    evaluate_fit_score_band,
    evaluate_job_match,
    evaluate_reasoning_quality,
    evaluate_signal_alignment,
    evaluate_structured_explanations,
)
from agent.prompts.prompt_manager import PromptManager
from agent.schemas.pipeline_job import PipelineJob


class FakePrompt:
    metadata = {
        "lc_hub_owner": "personal",
        "lc_hub_repo": "job-evaluation",
        "lc_hub_commit_hash": "commit-123",
    }

    def invoke(self, variables):
        class Value:
            def __init__(self, value: str) -> None:
                self.value = value

            def to_string(self) -> str:
                return self.value

        return Value(f"Hub prompt for {variables['job_title']}")


class FakeClient:
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.requests = []

    def pull_prompt(self, identifier: str):
        self.requests.append(identifier)
        if self.should_fail:
            raise RuntimeError("boom")
        return FakePrompt()


def build_prompt_manager(client=None):
    return PromptManager(
        client=client,
        eval_prompt_identifier="workspace/job-evaluation:prod",
        eval_prompt_name="job-evaluation",
        eval_prompt_version="local-v1",
        eval_prompt_variant="default",
        memory_prompt_identifier="workspace/memory-summary:prod",
        memory_prompt_name="memory-summary",
        memory_prompt_version="local-v1",
        memory_prompt_variant="default",
    )


def test_prompt_manager_loads_langsmith_prompt_metadata():
    manager = build_prompt_manager(client=FakeClient())

    rendered = manager.render_evaluation_prompt(
        user_context={
            "profile_data": {"role": "Machine Learning Engineer", "years_of_experience": 6},
            "guidelines": {"must_haves": ["Python"], "deal_breakers": []},
        },
        recent_memory="Avoid weak infra roles.",
        job=PipelineJob(
            job_id="18f3fb52-d02c-4f2a-b0df-20467365ad27",
            platform="test_source",
            external_job_id="job-001",
            title="Senior Machine Learning Engineer",
            company="Signal Labs",
            jd_raw_text="Build production ML systems.",
            url="https://example.com/jobs/job-001",
        ),
    )

    assert rendered.text == "Hub prompt for Senior Machine Learning Engineer"
    assert rendered.metadata.source == "langsmith"
    assert rendered.metadata.prompt_version == "prod"
    assert rendered.metadata.prompt_name == "job-evaluation"
    assert rendered.metadata.prompt_identifier == "workspace/job-evaluation:prod"
    assert rendered.metadata.prompt_reference == "prod"
    assert rendered.metadata.prompt_tag == "prod"
    assert rendered.metadata.prompt_commit_hash == "commit-123"
    assert rendered.metadata.prompt_owner == "personal"
    assert rendered.metadata.prompt_repo == "job-evaluation"


def test_prompt_manager_falls_back_to_local_prompt_when_hub_load_fails():
    manager = build_prompt_manager(client=FakeClient(should_fail=True))

    rendered = manager.render_evaluation_prompt(
        user_context={
            "profile_data": {"role": "Machine Learning Engineer", "years_of_experience": 6},
            "guidelines": {"must_haves": ["Python"], "deal_breakers": ["contract-only"]},
        },
        recent_memory="Avoid weak infra roles.",
        job=PipelineJob(
            job_id="18f3fb52-d02c-4f2a-b0df-20467365ad27",
            platform="test_source",
            external_job_id="job-001",
            title="Senior Machine Learning Engineer",
            company="Signal Labs",
            jd_raw_text="Build production ML systems.",
            url="https://example.com/jobs/job-001",
        ),
    )

    assert "Machine Learning Engineer" in rendered.text
    assert "contract-only" in rendered.text
    assert rendered.metadata.source == "local"
    assert rendered.metadata.prompt_version == "local-v1"
    assert rendered.metadata.prompt_identifier == ""
    assert rendered.metadata.requested_prompt_identifier == "workspace/job-evaluation:prod"
    assert rendered.metadata.prompt_reference == "prod"


def test_memory_summary_render_returns_metadata():
    manager = build_prompt_manager(client=None)
    rendered = manager.render_memory_summary(["salary too low", "salary too low", "pure frontend"])

    assert "salary too low" in rendered.text
    assert rendered.metadata.prompt_name == "memory-summary"
    assert rendered.metadata.prompt_version == "local-v1"


def test_curated_dataset_fixture_and_rule_based_evaluators():
    examples = load_curated_examples(
        Path("src/agent/evals/fixtures/job_eval_gold.json")
    )
    assert len(examples) >= 5

    class Run:
        outputs = {
            "fit_score": 88,
            "summary": "Strong fit\nMatches must-haves",
            "strengths": ["Python strength", "SQL strength", "MLOps strength"],
            "concerns": [],
            "must_have_matches": ["Python", "SQL", "MLOps"],
            "deal_breaker_flags": [],
            "confidence": "HIGH",
        }

    class Example:
        outputs = examples[0]["outputs"]

    assert evaluate_job_match(Run(), Example()).score == 1
    assert evaluate_fit_score_band(Run(), Example()).score == 1
    assert evaluate_reasoning_quality(Run(), Example()).score == 1
    signal_alignment = evaluate_signal_alignment(Run(), Example())
    assert signal_alignment["results"][0].score == 1
    assert signal_alignment["results"][1].score == 1
    structured_alignment = evaluate_structured_explanations(Run(), Example())
    assert structured_alignment["results"][0].score == 1
    assert structured_alignment["results"][1].score == 1
    assert structured_alignment["results"][2].score == 1
