from agent.prompts.evaluation_prompt import build_evaluation_prompt
from agent.schemas.pipeline_job import PipelineJob


def test_build_evaluation_prompt_includes_guidelines_and_recent_memory():
    prompt = build_evaluation_prompt(
        user_context={
            "profile_data": {"role": "Machine Learning Engineer", "years_of_experience": 6},
            "guidelines": {
                "must_haves": ["Python", "SQL"],
                "deal_breakers": ["contract-only"],
            },
        },
        recent_memory="Avoid jobs with weak infra ownership.",
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

    assert "Machine Learning Engineer" in prompt
    assert "Python, SQL" in prompt
    assert "contract-only" in prompt
    assert "Avoid jobs with weak infra ownership." in prompt
    assert "fit_score" in prompt
    assert "마크다운 코드펜스나 추가 설명은 절대 포함하지 마세요." in prompt
