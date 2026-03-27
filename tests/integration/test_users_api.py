from tests.conftest import auth_headers


async def test_profile_get_and_update_round_trip(client):
    get_response = await client.get(
        "/api/v1/users/me/profile",
        headers=auth_headers(),
    )

    assert get_response.status_code == 200
    assert get_response.json()["email"] == "scaffold-user@example.com"
    assert get_response.json()["profile_data"]["role"] == ""
    assert get_response.json()["profile_data"]["title_keywords"] == []
    assert get_response.json()["guidelines"]["must_haves"] == []
    assert get_response.json()["notification_settings"]["minimum_fit_score"] == 80
    assert get_response.json()["notification_settings"]["delivery_channel"] is None

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
    assert update_response.json()["profile_data"]["role"] == "Machine Learning Engineer"
    assert update_response.json()["guidelines"]["must_haves"] == ["Python", "SQL"]
    assert update_response.json()["notification_settings"]["minimum_fit_score"] == 82

    second_get_response = await client.get(
        "/api/v1/users/me/profile",
        headers=auth_headers(),
    )

    assert second_get_response.status_code == 200
    assert second_get_response.json()["profile_data"]["years_of_experience"] == 6
    assert second_get_response.json()["guidelines"]["deal_breakers"] == ["contract-only"]


async def test_profile_normalizes_whitespace_and_duplicates(client):
    response = await client.put(
        "/api/v1/users/me/profile",
        headers=auth_headers(),
        json={
            "profile_data": {
                "role": "  Machine Learning Engineer  ",
                "years_of_experience": 6,
                "title_keywords": [" ML ", "ml", " ai "],
            },
            "guidelines": {
                "must_haves": [" Python ", "", "python", " SQL "],
                "deal_breakers": [" contract-only ", "contract-only", " "],
            },
            "notification_settings": {"minimum_fit_score": 80, "delivery_channel": " slack "},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["profile_data"]["role"] == "Machine Learning Engineer"
    assert body["profile_data"]["title_keywords"] == ["ML", "ai"]
    assert body["guidelines"]["must_haves"] == ["Python", "SQL"]
    assert body["guidelines"]["deal_breakers"] == ["contract-only"]
    assert body["notification_settings"]["delivery_channel"] == "slack"


async def test_profile_rejects_invalid_payload_shape(client):
    response = await client.put(
        "/api/v1/users/me/profile",
        headers=auth_headers(),
        json={
            "profile_data": {
                "role": "   ",
                "years_of_experience": -1,
                "title_keywords": "machine learning",
            },
            "guidelines": {
                "must_haves": ["Python", 123],
                "deal_breakers": "contract-only",
            },
            "notification_settings": {"minimum_fit_score": 120},
        },
    )

    assert response.status_code == 422


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


async def test_profile_requires_real_bearer_token(client, monkeypatch):
    import api.dependencies.auth as auth_module
    from fastapi import HTTPException, status

    class RejectingVerifier:
        def verify_access_token(self, token: str):
            del token
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid bearer token.",
            )

    monkeypatch.setattr(auth_module, "get_token_verifier", lambda: RejectingVerifier())

    response = await client.get(
        "/api/v1/users/me/profile",
        headers={"Authorization": "Bearer not-valid"},
    )

    assert response.status_code == 401


async def test_profile_rejects_missing_bearer_token(client):
    response = await client.get("/api/v1/users/me/profile")

    assert response.status_code == 401
