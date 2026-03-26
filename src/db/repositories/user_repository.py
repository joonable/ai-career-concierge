from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, select

from db.models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.session.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def list_all(self) -> List[User]:
        return list(self.session.exec(select(User)).all())

    def upsert_from_identity(
        self,
        email: str,
        oauth_id: str,
        preferred_user_id: Optional[UUID] = None,
    ) -> User:
        user = self.get_by_email(email)
        if user is None:
            user_kwargs = {
                "email": email,
                "oauth_id": oauth_id,
            }
            if preferred_user_id is not None:
                user_kwargs["id"] = preferred_user_id
            user = User(**user_kwargs)
            self.session.add(user)
        else:
            user.oauth_id = oauth_id
            user.updated_at = datetime.now(timezone.utc)

        self.session.commit()
        self.session.refresh(user)
        return user

    def update_profile(
        self,
        user: User,
        profile_data: Dict[str, Any],
        guidelines: Dict[str, Any],
        notification_settings: Dict[str, Any],
    ) -> User:
        user.profile_data = profile_data
        user.guidelines = guidelines
        user.notification_settings = notification_settings
        user.updated_at = datetime.now(timezone.utc)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
