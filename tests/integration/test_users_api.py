from tests.conftest import auth_headers


async def test_profile_get_and_update_round_trip(client):
    get_response = await client.get(
        "/api/v1/users/me/profile",
        headers=auth_headers(),
    )

    assert get_response.status_code == 200
    assert get_response.json()["email"] == "scaffold-user@example.com"

    update_response = await client.put(
        "/api/v1/users/me/profile",
        headers=auth_headers(),
        json={
            "profile_data": {
                "role": "Machine Learning Engineer",
                "years_of_experience": 6,
                "title_keywords": ["machine learning", "ml"],
            },
            "guidelines": {
                "must_haves": ["Python", "SQL"],
                "deal_breakers": ["contract-only"],
            },
            "notification_settings": {"minimum_fit_score": 82},
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["notification_settings"]["minimum_fit_score"] == 82


async def test_feedback_and_dashboard_api(client, db_session):
    from tests.conftest import auth_headers, seed_job_and_evaluation, seed_user

    user = seed_user(db_session)
    _, evaluation = seed_job_and_evaluation(db_session, user)

    feedback_response = await client.post(
        f"/api/v1/evaluations/{evaluation.id}/feedback",
        headers=auth_headers(),
        json={"feedback": "DISLIKE", "feedback_reason": "salary too low"},
    )

    assert feedback_response.status_code == 200
    assert feedback_response.json()["feedback"] == "DISLIKE"

    dashboard_response = await client.get("/api/v1/users/me/dashboard", headers=auth_headers())

    assert dashboard_response.status_code == 200
    recommendation = dashboard_response.json()["recommendations"][0]
    assert recommendation["feedback_reason"] == "salary too low"
    assert recommendation["title"] == "Senior Machine Learning Engineer"
