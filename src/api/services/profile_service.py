from __future__ import annotations

from api.dependencies.auth import UserIdentity
from api.schemas.users import (
    UserProfilePayload,
    UserProfileResponse,
)


class ProfileService:
    def __init__(self, user_store):
        self.user_store = user_store

    def get_profile(self, identity: UserIdentity) -> UserProfileResponse:
        return self.user_store.upsert_from_identity(identity)

    def update_profile(
        self,
        identity: UserIdentity,
        payload: UserProfilePayload,
    ) -> UserProfileResponse:
        return self.user_store.update_profile(identity, payload)
