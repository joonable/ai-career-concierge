from __future__ import annotations

from functools import lru_cache
from typing import Optional
from uuid import UUID

import jwt
from fastapi import Header, HTTPException, status
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

from common.config import Settings, get_settings


class UserIdentity(BaseModel):
    user_id: Optional[UUID] = None
    email: str
    oauth_id: str


class SupabaseJWTVerifier:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.jwks_client = PyJWKClient(settings.supabase_jwks_url)

    def verify_access_token(self, token: str) -> UserIdentity:
        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256", "ES256"],
                issuer=self.settings.supabase_issuer,
                options={"verify_aud": False},
            )
        except InvalidTokenError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid bearer token.",
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to verify bearer token.",
            ) from exc

        oauth_id = payload.get("sub")
        email = payload.get("email")
        if not oauth_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer token is missing required claims.",
            )

        user_id: Optional[UUID] = None
        try:
            user_id = UUID(str(oauth_id))
        except ValueError:
            user_id = None

        return UserIdentity(user_id=user_id, email=email, oauth_id=str(oauth_id))


@lru_cache(maxsize=1)
def get_token_verifier() -> SupabaseJWTVerifier:
    return SupabaseJWTVerifier(get_settings())


def get_current_user_identity(
    authorization: Optional[str] = Header(default=None),
) -> UserIdentity:
    if authorization is None or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")

    token = authorization.split(" ", 1)[1].strip()
    return get_token_verifier().verify_access_token(token)
