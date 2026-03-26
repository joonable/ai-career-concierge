from __future__ import annotations

from typing import Dict

from api.dependencies.auth import UserIdentity
from api.schemas.users import UserProfilePayload, UserProfileResponse
from db.repositories import UserRepository


class ProfileService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_profile(self, identity: UserIdentity) -> UserProfileResponse:
        user = self.user_repository.upsert_from_identity(
            email=identity.email,
            oauth_id=identity.oauth_id,
            preferred_user_id=identity.user_id,
        )
        notification_settings = user.notification_settings or {"minimum_fit_score": 80}
        return UserProfileResponse(
            user_id=user.id,
            email=user.email,
            profile_data=user.profile_data,
            guidelines=user.guidelines,
            notification_settings=notification_settings,
        )

    def update_profile(
        self,
        identity: UserIdentity,
        payload: UserProfilePayload,
    ) -> UserProfileResponse:
        user = self.user_repository.upsert_from_identity(
            email=identity.email,
            oauth_id=identity.oauth_id,
            preferred_user_id=identity.user_id,
        )
        updated_user = self.user_repository.update_profile(
            user=user,
            profile_data=payload.profile_data,
            guidelines=payload.guidelines,
            notification_settings=_ensure_notification_defaults(payload.notification_settings),
        )
        return UserProfileResponse(
            user_id=updated_user.id,
            email=updated_user.email,
            profile_data=updated_user.profile_data,
            guidelines=updated_user.guidelines,
            notification_settings=updated_user.notification_settings,
        )


def _ensure_notification_defaults(notification_settings: Dict[str, object]) -> Dict[str, object]:
    merged = {"minimum_fit_score": 80}
    merged.update(notification_settings)
    return merged
