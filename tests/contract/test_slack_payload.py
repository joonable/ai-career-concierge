from agent.schemas.evaluation_result import LLMEvaluationResult
from api.services.slack_notifier import build_recommendation_payload


def test_slack_payload_contains_required_job_fields():
    payload = build_recommendation_payload(
        user_context={"dashboard_url": "http://localhost:3000/dashboard"},
        evaluation_result=LLMEvaluationResult.model_validate(
            {
                "evaluation_id": "1f7534c9-2dd0-46d9-85bb-4c9c8ca677cb",
                "job_id": "5fa5f963-dad6-4e05-84c8-e44da4c2d6a5",
                "platform": "test_source",
                "title": "Senior Machine Learning Engineer",
                "company": "Signal Labs",
                "url": "https://example.com/jobs/1",
                "fit_score": 91,
                "reasoning": "High signal match",
                "must_have_hits": [],
                "deal_breakers_found": [],
            }
        ),
    )

    assert "Signal Labs" in payload["text"]
    assert payload["blocks"][0]["text"]["text"].find("Fit score: *91*") != -1
    assert payload["blocks"][2]["elements"][0]["url"] == "http://localhost:3000/dashboard"
