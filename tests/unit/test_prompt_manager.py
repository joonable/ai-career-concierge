from pathlib import Path

from agent.evals.dataset_workflow import load_curated_examples
from agent.evals.rule_based_evaluators import (
    evaluate_fit_score_band,
    evaluate_job_match,
    evaluate_reasoning_quality,
    evaluate_score_policy_alignment,
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


def test_local_v3_prompt_contains_score_policy_and_structured_axes():
    manager = build_prompt_manager(client=FakeClient(should_fail=True))

    rendered = manager.render_evaluation_prompt(
        user_context={
            "profile_data": {"role": "Machine Learning Engineer", "years_of_experience": 6},
            "guidelines": {
                "must_haves": ["Python", "SQL", "MLOps"],
                "deal_breakers": ["contract-only", "onsite-only"],
            },
        },
        recent_memory="Avoid weak infra ownership.",
        job=PipelineJob(
            job_id="18f3fb52-d02c-4f2a-b0df-20467365ad27",
            platform="test_source",
            external_job_id="job-001",
            title="Backend Engineer, Model Serving",
            company="Signal Labs",
            jd_raw_text="Build inference APIs and deployment tooling.",
            url="https://example.com/jobs/job-001",
        ),
    )

    assert rendered.metadata.schema_version == "3"
    assert "`80~100`" in rendered.text
    assert "선호 title keywords" in rendered.text
    assert "알림 최소 적합도 기준" in rendered.text
    assert "구조화된 JD 책임 근거" in rendered.text
    assert "누락/불명확한 컨텍스트" in rendered.text
    assert "인접 직무 판단 규칙" in rendered.text
    assert "기본값은 `40~59`로 두고" in rendered.text
    assert "must-have 판단 규칙" in rendered.text
    assert "deal-breaker 판단 규칙" in rendered.text
    assert "transferable skill 판단 규칙" in rendered.text
    assert '"role_alignment"' in rendered.text
    assert '"must_have_coverage"' in rendered.text
    assert '"deal_breaker_severity"' in rendered.text
    assert '"transferable_skills"' in rendered.text


def test_prompt_manager_uses_normalized_context_values_in_rendered_prompt():
    manager = build_prompt_manager(client=FakeClient(should_fail=True))

    rendered = manager.render_evaluation_prompt(
        user_context={
            "profile_data": {
                "role": "Machine Learning Engineer",
                "years_of_experience": 6,
                "title_keywords": ["MLE", "Platform"],
            },
            "guidelines": {
                "must_haves": ["Python", "SQL"],
                "deal_breakers": ["contract-only"],
            },
            "notification_settings": {"minimum_fit_score": 80},
        },
        recent_memory="weak infra ownership; contract-only roles",
        job=PipelineJob(
            job_id="18f3fb52-d02c-4f2a-b0df-20467365ad27",
            platform="test_source",
            external_job_id="job-001",
            title="Backend Engineer, Model Serving",
            company="Signal Labs",
            jd_raw_text="Build inference APIs and deployment tooling.",
            url="https://example.com/jobs/job-001",
            source_metadata={
                "responsibilities": ["Build inference APIs"],
                "requirements": ["Python", "Kubernetes"],
                "location": "Seoul",
                "employment_type": "full-time",
            },
        ),
    )

    assert "MLE, Platform" in rendered.text
    assert "알림 최소 적합도 기준: 80" in rendered.text
    assert "Build inference APIs" in rendered.text
    assert "Seoul" in rendered.text
    assert "No major missing context." in rendered.text


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
    assert len(examples) >= 15
    assert examples[0]["metadata"]["scenario_family"]
    assert examples[0]["outputs"]["scoring_note"]
    assert examples[0]["outputs"]["expected_role_alignment"] in {"HIGH", "MEDIUM", "LOW"}
    assert examples[0]["outputs"]["expected_must_have_coverage"] in {"STRONG", "PARTIAL", "WEAK"}
    assert examples[0]["outputs"]["expected_deal_breaker_severity"] in {"NONE", "SOFT", "HARD"}
    assert examples[0]["outputs"]["expected_transferable_skill_level"] in {"HIGH", "MEDIUM", "LOW"}

    class Run:
        outputs = {
            "fit_score": 88,
            "summary": "Strong fit\nMatches must-haves",
            "strengths": ["Python strength", "SQL strength", "MLOps strength"],
            "concerns": [],
            "must_have_matches": ["Python", "SQL", "MLOps"],
            "deal_breaker_flags": [],
            "confidence": "HIGH",
            "role_alignment": "HIGH",
            "must_have_coverage": "STRONG",
            "deal_breaker_severity": "NONE",
            "transferable_skill_level": "HIGH",
        }

    class Example:
        outputs = examples[0]["outputs"]

    assert evaluate_job_match(Run(), Example()).score == 1
    assert evaluate_fit_score_band(Run(), Example()).score == 1
    assert evaluate_reasoning_quality(Run(), Example()).score == 1
    score_policy_alignment = evaluate_score_policy_alignment(Run(), Example())
    assert score_policy_alignment["results"][0].score == 1
    assert score_policy_alignment["results"][1].score == 1
    assert score_policy_alignment["results"][2].score == 1
    assert score_policy_alignment["results"][3].score == 1
    assert score_policy_alignment["results"][4].score == 1
    signal_alignment = evaluate_signal_alignment(Run(), Example())
    assert signal_alignment["results"][0].score == 1
    assert signal_alignment["results"][1].score == 1
    structured_alignment = evaluate_structured_explanations(Run(), Example())
    assert structured_alignment["results"][0].score == 1
    assert structured_alignment["results"][1].score == 1
    assert structured_alignment["results"][2].score == 1


def test_score_policy_alignment_flags_hard_reject_penalty_failures():
    examples = load_curated_examples(
        Path("src/agent/evals/fixtures/job_eval_gold.json")
    )

    hard_reject_example = next(
        example for example in examples if example["outputs"]["expected_deal_breaker_severity"] == "HARD"
    )

    class Run:
        outputs = {
            "fit_score": 91,
            "role_alignment": hard_reject_example["outputs"]["expected_role_alignment"],
            "must_have_coverage": hard_reject_example["outputs"]["expected_must_have_coverage"],
            "deal_breaker_severity": hard_reject_example["outputs"]["expected_deal_breaker_severity"],
            "transferable_skill_level": hard_reject_example["outputs"]["expected_transferable_skill_level"],
        }

    class Example:
        outputs = hard_reject_example["outputs"]

    score_policy_alignment = evaluate_score_policy_alignment(Run(), Example())

    assert score_policy_alignment["results"][0].score == 1
    assert score_policy_alignment["results"][1].score == 1
    assert score_policy_alignment["results"][2].score == 1
    assert score_policy_alignment["results"][3].score == 1
    assert score_policy_alignment["results"][4].score == 0
