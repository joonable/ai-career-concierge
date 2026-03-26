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
            "reasoning": "Strong ML systems fit / matches core stack",
            "must_have_hits": ["Python", "SQL"],
            "deal_breakers_found": [],
        }
    )

    assert payload.fit_score == 92
    assert payload.company == "Signal Labs"


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
                "reasoning": "Bad payload",
            }
        )
