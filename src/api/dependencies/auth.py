from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import Header, HTTPException, status
from pydantic import BaseModel

from common.config import AppEnv, Settings, get_settings


class UserIdentity(BaseModel):
    user_id: Optional[UUID] = None
    email: str
    oauth_id: str


def get_current_user_identity(
    authorization: Optional[str] = Header(default=None),
    x_user_email: Optional[str] = Header(default=None),
    x_user_id: Optional[str] = Header(default=None),
) -> UserIdentity:
    settings: Settings = get_settings()
    if authorization is None or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")

    token = authorization.split(" ", 1)[1].strip()
    if settings.app_env in (AppEnv.DEVELOPMENT, AppEnv.TEST) and token == "dev-token":
        user_id = UUID(x_user_id) if x_user_id else None
        email = x_user_email or "scaffold-user@example.com"
        return UserIdentity(
            user_id=user_id,
            email=email,
            oauth_id=f"dev-oauth:{email}",
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Supabase JWT verification is not configured in scaffold mode.",
    )
