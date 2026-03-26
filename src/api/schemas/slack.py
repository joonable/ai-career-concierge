from pydantic import BaseModel


class SlackWebhookResponse(BaseModel):
    ok: bool = True
