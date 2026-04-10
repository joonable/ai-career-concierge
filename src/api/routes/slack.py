from __future__ import annotations

import json
from urllib.parse import parse_qs

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from api.dependencies.runtime import get_runtime
from api.dependencies.supabase_store import get_evaluation_store, get_user_store
from api.schemas.slack import SlackWebhookResponse
from api.services.feedback_service import FeedbackService

router = APIRouter(prefix="/api/v1/slack", tags=["slack"])


@router.post("/interactive-webhook", response_model=SlackWebhookResponse)
async def interactive_webhook(
    request: Request,
    x_slack_request_timestamp: str = Header(alias="X-Slack-Request-Timestamp"),
    x_slack_signature: str = Header(alias="X-Slack-Signature"),
    user_store=Depends(get_user_store),
    evaluation_store=Depends(get_evaluation_store),
    runtime=Depends(get_runtime),
) -> SlackWebhookResponse:
    raw_body = await request.body()
    if not runtime.slack_signature_service.verify(
        timestamp=x_slack_request_timestamp,
        signature=x_slack_signature,
        body=raw_body,
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Slack signature.")

    content_type = request.headers.get("content-type", "")
    if "application/x-www-form-urlencoded" in content_type:
        payload = parse_qs(raw_body.decode("utf-8")).get("payload", ["{}"])[0]
        parsed_payload = json.loads(payload)
    else:
        parsed_payload = json.loads(raw_body.decode("utf-8"))

    service = FeedbackService(
        user_store=user_store,
        evaluation_store=evaluation_store,
    )
    service.record_feedback_from_slack(parsed_payload)
    return SlackWebhookResponse(ok=True)
