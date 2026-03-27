from __future__ import annotations

from api.dependencies.auth import UserIdentity
from api.schemas.users import (
    Guidelines,
    NotificationSettings,
    ProfileData,
    UserProfilePayload,
    UserProfileResponse,
)
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
        return UserProfileResponse(
            user_id=user.id,
            email=user.email,
            profile_data=_build_profile_data(user.profile_data),
            guidelines=_build_guidelines(user.guidelines),
            notification_settings=_build_notification_settings(user.notification_settings),
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
            profile_data=payload.profile_data.model_dump(),
            guidelines=payload.guidelines.model_dump(),
            notification_settings=payload.notification_settings.model_dump(exclude_none=True),
        )
        return UserProfileResponse(
            user_id=updated_user.id,
            email=updated_user.email,
            profile_data=_build_profile_data(updated_user.profile_data),
            guidelines=_build_guidelines(updated_user.guidelines),
            notification_settings=_build_notification_settings(updated_user.notification_settings),
        )


def _build_profile_data(profile_data: object) -> ProfileData:
    merged = {
        "role": "",
        "years_of_experience": 0,
        "title_keywords": [],
    }
    if isinstance(profile_data, dict):
        merged.update(profile_data)
    return ProfileData.model_construct(**merged)


def _build_guidelines(guidelines: object) -> Guidelines:
    merged = {
        "must_haves": [],
        "deal_breakers": [],
    }
    if isinstance(guidelines, dict):
        merged.update(guidelines)
    return Guidelines.model_construct(**merged)


def _build_notification_settings(notification_settings: object) -> NotificationSettings:
    merged = {
        "minimum_fit_score": 80,
        "delivery_channel": None,
    }
    if isinstance(notification_settings, dict):
        merged.update(notification_settings)
    return NotificationSettings.model_construct(**merged)
