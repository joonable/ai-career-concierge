async def test_slack_interactive_webhook_updates_feedback(client, db_session):
    from tests.conftest import seed_job_and_evaluation, seed_user, sign_slack_body, slack_json_payload

    user = seed_user(db_session)
    _, evaluation = seed_job_and_evaluation(db_session, user)

    body = slack_json_payload(str(evaluation.id), "LIKE")
    headers = sign_slack_body("dev-slack-secret", body)

    response = await client.post(
        "/api/v1/slack/interactive-webhook",
        headers=headers,
        content=body,
    )

    assert response.status_code == 200
    assert response.json()["ok"] is True
