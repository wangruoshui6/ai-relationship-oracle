from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile


class UserProfileRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_id(self, user_id: str) -> UserProfile | None:
        return self.db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))

    def save(self, profile: UserProfile) -> UserProfile:
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
