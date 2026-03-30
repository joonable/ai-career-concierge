from datetime import datetime, timedelta, timezone

from tests.conftest import auth_headers


async def test_profile_get_and_update_round_trip(client, db_session):
    from db.models import User
    from uuid import UUID

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
    assert get_response.json()["notification_settings"]["delivery_channel"] == "slack"

    stored_user = db_session.get(User, UUID(get_response.json()["user_id"]))
    assert stored_user is not None
    assert stored_user.profile_data == get_response.json()["profile_data"]
    assert stored_user.guidelines == get_response.json()["guidelines"]
    assert stored_user.notification_settings == get_response.json()["notification_settings"]

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
    assert update_response.json()["notification_settings"]["delivery_channel"] == "slack"

    second_get_response = await client.get(
        "/api/v1/users/me/profile",
        headers=auth_headers(),
    )

    assert second_get_response.status_code == 200
    assert second_get_response.json()["profile_data"]["years_of_experience"] == 6
    assert second_get_response.json()["guidelines"]["deal_breakers"] == ["contract-only"]

    db_session.expire_all()
    updated_user = db_session.get(User, UUID(update_response.json()["user_id"]))
    assert updated_user is not None
    assert updated_user.profile_data == second_get_response.json()["profile_data"]
    assert updated_user.guidelines == second_get_response.json()["guidelines"]
    assert updated_user.notification_settings == second_get_response.json()["notification_settings"]


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


async def test_profile_update_derives_internal_defaults_for_onboarding_fields(client, db_session):
    from db.models import User
    from uuid import UUID

    response = await client.put(
        "/api/v1/users/me/profile",
        headers=auth_headers(),
        json={
            "profile_data": {
                "role": "Machine Learning Engineer",
                "years_of_experience": 6,
            },
            "guidelines": {
                "must_haves": ["Python", "SQL"],
                "deal_breakers": ["contract-only"],
            },
            "notification_settings": {"minimum_fit_score": 85},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["profile_data"]["title_keywords"] == ["machine learning engineer"]
    assert body["notification_settings"]["delivery_channel"] == "slack"

    db_session.expire_all()
    stored_user = db_session.get(User, UUID(body["user_id"]))
    assert stored_user is not None
    assert stored_user.profile_data == body["profile_data"]
    assert stored_user.guidelines == body["guidelines"]
    assert stored_user.notification_settings == body["notification_settings"]


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


async def test_profile_rejects_unsupported_delivery_channel(client):
    response = await client.put(
        "/api/v1/users/me/profile",
        headers=auth_headers(),
        json={
            "profile_data": {
                "role": "Machine Learning Engineer",
                "years_of_experience": 6,
            },
            "guidelines": {
                "must_haves": ["Python"],
                "deal_breakers": [],
            },
            "notification_settings": {
                "minimum_fit_score": 80,
                "delivery_channel": "email",
            },
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
    assert recommendation["company"] == "Signal Labs"
    assert recommendation["platform"] == "test_source"
    assert recommendation["url"] == "https://example.com/jobs/seed-job"
    assert recommendation["jd_raw_text"] == "Python SQL recommender systems and ML platform ownership."
    assert recommendation["min_years_experience"] == 5
    assert recommendation["max_years_experience"] == 8
    assert recommendation["source_metadata"] == {}
    assert recommendation["fit_score"] is None
    assert recommendation["reasoning"] is None
    assert recommendation["decision_summary"] == "규칙 필터는 통과했지만 아직 LLM 정밀 평가가 끝나지 않아 추가 확인이 필요합니다."
    assert "필수 조건 일치: Python" in recommendation["match_highlights"]
    assert "필수 조건 일치: SQL" in recommendation["match_highlights"]
    assert "직무 키워드가 공고 제목과 일치합니다." in recommendation["match_highlights"]
    assert "경력 6년이 권장 범위 5년 ~ 8년에 들어옵니다." in recommendation["match_highlights"]
    assert recommendation["risk_highlights"] == [
        "JD에 구조화된 요구사항이 부족해 사람이 한 번 더 확인하는 편이 안전합니다."
    ]
    assert recommendation["confidence_level"] == "LOW"
    assert recommendation["rule_rejection_reason"] is None
    assert recommendation["rule_match_reasons"] == [
        "목표 직무 'Machine Learning Engineer' 기준에서 공고 제목이 관련 키워드와 일치합니다.",
        "현재 경력 6년이 권장 범위 5년 ~ 8년 안에 있습니다.",
    ]
    assert recommendation["rule_rejection_details"] == []
    assert recommendation["responsibilities"] == ["Python SQL recommender systems and ML platform ownership"]
    assert recommendation["requirements"] == [
        "Python 경험",
        "SQL 경험",
        "recommender systems 경험",
        "권장 경력 5년 ~ 8년",
    ]
    assert recommendation["preferred_requirements"] == []
    assert recommendation["location"] is None
    assert recommendation["employment_type"] is None
    assert recommendation["created_at"]
    assert recommendation["updated_at"]


async def test_dashboard_returns_empty_recommendations_for_new_user(client):
    response = await client.get("/api/v1/users/me/dashboard", headers=auth_headers())

    assert response.status_code == 200
    assert response.json()["recommendations"] == []


async def test_dashboard_only_returns_rows_for_the_current_user(client, db_session):
    from db.models import Evaluation, Job
    from tests.conftest import seed_user

    current_user = seed_user(db_session, email="scaffold-user@example.com")
    other_user = seed_user(db_session, email="other-user@example.com")
    current_job = Job(
        platform="linkedin",
        external_job_id="current-job",
        title="Current User Role",
        company="Alpha",
        jd_raw_text="Python SQL",
        url="https://example.com/jobs/current",
        min_years_experience=5,
        max_years_experience=8,
        source_metadata={},
    )
    other_job = Job(
        platform="wanted",
        external_job_id="other-job",
        title="Other User Role",
        company="Beta",
        jd_raw_text="Python SQL",
        url="https://example.com/jobs/other",
        min_years_experience=5,
        max_years_experience=8,
        source_metadata={},
    )
    db_session.add(current_job)
    db_session.add(other_job)
    db_session.commit()
    db_session.refresh(current_job)
    db_session.refresh(other_job)

    current_evaluation = Evaluation(user_id=current_user.id, job_id=current_job.id)
    other_evaluation = Evaluation(user_id=other_user.id, job_id=other_job.id)

    current_evaluation.reasoning = "Current user recommendation"
    other_evaluation.reasoning = "Other user recommendation"
    db_session.add(current_evaluation)
    db_session.add(other_evaluation)
    db_session.commit()

    response = await client.get("/api/v1/users/me/dashboard", headers=auth_headers())

    assert response.status_code == 200
    recommendations = response.json()["recommendations"]
    assert len(recommendations) == 1
    assert recommendations[0]["reasoning"] == "Current user recommendation"


async def test_dashboard_returns_recommendations_in_updated_order(client, db_session):
    from db.models import Evaluation, Job
    from tests.conftest import seed_user

    user = seed_user(db_session)
    first_job = Job(
        platform="linkedin",
        external_job_id="job-1",
        title="First Role",
        company="Alpha",
        jd_raw_text="Python SQL",
        url="https://example.com/jobs/1",
        min_years_experience=5,
        max_years_experience=8,
        source_metadata={},
    )
    second_job = Job(
        platform="wanted",
        external_job_id="job-2",
        title="Second Role",
        company="Beta",
        jd_raw_text="Python SQL",
        url="https://example.com/jobs/2",
        min_years_experience=5,
        max_years_experience=8,
        source_metadata={},
    )
    db_session.add(first_job)
    db_session.add(second_job)
    db_session.commit()
    db_session.refresh(first_job)
    db_session.refresh(second_job)

    older_evaluation = Evaluation(
        user_id=user.id,
        job_id=first_job.id,
        reasoning="Older recommendation",
        updated_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    newer_evaluation = Evaluation(
        user_id=user.id,
        job_id=second_job.id,
        reasoning="Newer recommendation",
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(older_evaluation)
    db_session.add(newer_evaluation)
    db_session.commit()

    response = await client.get("/api/v1/users/me/dashboard", headers=auth_headers())

    assert response.status_code == 200
    recommendations = response.json()["recommendations"]
    assert [item["title"] for item in recommendations] == ["Second Role", "First Role"]


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


async def test_dashboard_rejects_missing_bearer_token(client):
    response = await client.get("/api/v1/users/me/dashboard")

    assert response.status_code == 401
