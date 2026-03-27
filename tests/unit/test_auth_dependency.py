from fastapi import HTTPException

from api.dependencies.auth import SupabaseJWTVerifier, get_current_user_identity


def test_get_current_user_identity_requires_bearer_prefix():
    try:
        get_current_user_identity(authorization=None)
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        raise AssertionError("Expected HTTPException for missing bearer token.")


def test_supabase_verifier_rejects_missing_claims(monkeypatch):
    from common.config import Settings

    verifier = SupabaseJWTVerifier(
        Settings(
            APP_ENV="test",
            SUPABASE_URL="https://example.supabase.co",
            DATABASE_URL="sqlite:///./.data/test.db",
            INTERNAL_API_KEY="test",
            ALLOW_DEV_SCHEDULE=True,
        )
    )

    class FakeJWKClient:
        def get_signing_key_from_jwt(self, token: str):
            del token

            class FakeKey:
                key = "unused"

            return FakeKey()

    monkeypatch.setattr(verifier, "jwks_client", FakeJWKClient())
    monkeypatch.setattr(
        "api.dependencies.auth.jwt.decode",
        lambda *args, **kwargs: {"sub": "user-only"},
    )

    try:
        verifier.verify_access_token("token")
    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.detail == "Bearer token is missing required claims."
    else:
        raise AssertionError("Expected claim validation failure.")
