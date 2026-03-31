import pytest
from pydantic import ValidationError

from agent.schemas.evaluation_result import LLMEvaluationResult


def test_llm_evaluation_result_accepts_valid_payload():
    payload = LLMEvaluationResult.model_validate(
        {
            "evaluation_id": "1f7534c9-2dd0-46d9-85bb-4c9c8ca677cb",
            "job_id": "5fa5f963-dad6-4e05-84c8-e44da4c2d6a5",
            "platform": "test_source",
            "title": "Senior Machine Learning Engineer",
            "company": "Signal Labs",
            "url": "https://example.com/jobs/1",
            "fit_score": 92,
            "summary": "Strong ML systems fit / matches core stack",
            "strengths": ["Python match", "SQL match"],
            "concerns": ["Need location confirmation"],
            "must_have_matches": ["Python", "SQL"],
            "deal_breaker_flags": [],
            "confidence": "HIGH",
            "role_alignment": "HIGH",
            "must_have_coverage": "STRONG",
            "deal_breaker_severity": "NONE",
            "transferable_skills": "HIGH",
        }
    )

    assert payload.fit_score == 92
    assert payload.company == "Signal Labs"
    assert payload.reasoning == "Strong ML systems fit / matches core stack"
    assert payload.must_have_hits == ["Python", "SQL"]
    assert payload.role_alignment == "HIGH"
    assert payload.transferable_skills == "HIGH"


def test_llm_evaluation_result_accepts_legacy_transferable_skill_alias():
    payload = LLMEvaluationResult.model_validate(
        {
            "evaluation_id": "1f7534c9-2dd0-46d9-85bb-4c9c8ca677cb",
            "job_id": "5fa5f963-dad6-4e05-84c8-e44da4c2d6a5",
            "platform": "test_source",
            "title": "Senior Machine Learning Engineer",
            "company": "Signal Labs",
            "url": "https://example.com/jobs/1",
            "fit_score": 92,
            "summary": "Strong ML systems fit / matches core stack",
            "strengths": ["Python match", "SQL match"],
            "concerns": ["Need location confirmation"],
            "must_have_matches": ["Python", "SQL"],
            "deal_breaker_flags": [],
            "confidence": "HIGH",
            "role_alignment": "HIGH",
            "must_have_coverage": "STRONG",
            "deal_breaker_severity": "NONE",
            "transferable_skill_level": "HIGH",
        }
    )

    assert payload.transferable_skills == "HIGH"


def test_llm_evaluation_result_rejects_invalid_score():
    with pytest.raises(ValidationError):
        LLMEvaluationResult.model_validate(
            {
                "evaluation_id": "1f7534c9-2dd0-46d9-85bb-4c9c8ca677cb",
                "job_id": "5fa5f963-dad6-4e05-84c8-e44da4c2d6a5",
                "platform": "test_source",
                "title": "Senior Machine Learning Engineer",
                "company": "Signal Labs",
                "url": "https://example.com/jobs/1",
                "fit_score": 120,
                "summary": "Bad payload",
                "strengths": [],
                "concerns": [],
                "must_have_matches": [],
                "deal_breaker_flags": [],
                "confidence": "LOW",
                "role_alignment": "LOW",
                "must_have_coverage": "WEAK",
                "deal_breaker_severity": "NONE",
                "transferable_skills": "LOW",
            }
        )


def test_llm_evaluation_result_requires_score_policy_fields():
    with pytest.raises(ValidationError):
        LLMEvaluationResult.model_validate(
            {
                "evaluation_id": "1f7534c9-2dd0-46d9-85bb-4c9c8ca677cb",
                "job_id": "5fa5f963-dad6-4e05-84c8-e44da4c2d6a5",
                "platform": "test_source",
                "title": "Senior Machine Learning Engineer",
                "company": "Signal Labs",
                "url": "https://example.com/jobs/1",
                "fit_score": 88,
                "summary": "Missing intermediate judgments",
                "strengths": [],
                "concerns": [],
                "must_have_matches": [],
                "deal_breaker_flags": [],
                "confidence": "MEDIUM",
            }
        )
