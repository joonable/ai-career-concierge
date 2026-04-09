import json
from pathlib import Path

from agent.schemas.pipeline_job import PipelineJob
from promptops.projects.ai_career_concierge.context import build_normalized_evaluation_context


def test_build_normalized_evaluation_context_matches_fixture_contract():
    fixture = json.loads(Path("tests/fixtures/normalized_evaluation_context.json").read_text(encoding="utf-8"))

    normalized = build_normalized_evaluation_context(
        user_context=fixture["raw"]["user_context"],
        recent_memory=fixture["raw"]["recent_memory"],
        job=PipelineJob.model_validate(fixture["raw"]["job"]),
    )

    assert normalized.model_dump() == fixture["expected"]


def test_build_normalized_evaluation_context_surfaces_missingness():
    normalized = build_normalized_evaluation_context(
        user_context={
            "profile_data": {"role": "", "years_of_experience": None, "title_keywords": []},
            "guidelines": {"must_haves": [], "deal_breakers": []},
            "notification_settings": {},
        },
        recent_memory="",
        job=PipelineJob(
            job_id="18f3fb52-d02c-4f2a-b0df-20467365ad27",
            platform="test_source",
            external_job_id="job-001",
            title="",
            company="",
            jd_raw_text="",
            url="https://example.com/jobs/job-001",
            source_metadata={},
        ),
    )

    assert normalized.target_role == "unknown"
    assert normalized.missingness.missing_profile_fields == ["role", "years_of_experience"]
    assert normalized.missingness.missing_preference_fields == [
        "title_keywords",
        "must_haves",
        "deal_breakers",
        "minimum_fit_score",
    ]
    assert normalized.missingness.missing_job_fields == [
        "title",
        "company",
        "jd_raw_text",
        "responsibilities",
        "requirements",
    ]
    assert normalized.missingness.missing_memory is True
