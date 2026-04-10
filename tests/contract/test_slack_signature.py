from tests.conftest import sign_slack_body

from api.services.slack_signature_service import SlackSignatureService


def test_slack_signature_service_verifies_known_signature():
    service = SlackSignatureService("dev-slack-secret")
    body = b'{"ok": true}'
    headers = sign_slack_body(
        "dev-slack-secret",
        body,
        timestamp="1710000000",
    )

    assert service.verify(
        timestamp=headers["X-Slack-Request-Timestamp"],
        signature=headers["X-Slack-Signature"],
        body=body,
    )
