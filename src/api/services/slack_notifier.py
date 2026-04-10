from __future__ import annotations

from typing import Any, Dict, List

from common.logging import get_logger

logger = get_logger(__name__)


def build_recommendation_payload(
    *,
    user_context: Dict[str, Any],
    evaluation_result,
) -> Dict[str, Any]:
    dashboard_url = user_context.get("dashboard_url", "http://localhost:3000/dashboard")
    return {
        "text": f"{evaluation_result.title} at {evaluation_result.company}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*{evaluation_result.title}* at *{evaluation_result.company}*\n"
                        f"Fit score: *{evaluation_result.fit_score}*"
                    ),
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": evaluation_result.reasoning,
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Open dashboard"},
                        "url": dashboard_url,
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View job"},
                        "url": evaluation_result.url,
                    },
                ],
            },
        ],
    }


class LoggingSlackNotifier:
    def __init__(self):
        self.deliveries: List[Dict[str, Any]] = []

    async def send_recommendation(self, *, user_context: Dict[str, Any], evaluation_result) -> None:
        payload = build_recommendation_payload(
            user_context=user_context,
            evaluation_result=evaluation_result,
        )
        self.deliveries.append(payload)
        logger.info(
            "Prepared Slack delivery.",
            extra={
                "job_id": str(evaluation_result.job_id),
                "fit_score": evaluation_result.fit_score,
            },
        )
