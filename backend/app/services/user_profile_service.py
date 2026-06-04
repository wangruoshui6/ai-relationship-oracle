from sqlalchemy.orm import Session

from app.db.repositories.profile_repo import UserProfileRepo
from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileUpsertRequest
from app.services.bazi_profile_compute_service import BaziProfileComputeService


class UserProfileService:
    def __init__(self, db: Session) -> None:
        self.repo = UserProfileRepo(db)
        self.bazi_compute_service = BaziProfileComputeService()

    def get_by_user_id(self, user_id: str) -> UserProfile | None:
        return self.repo.get_by_user_id(user_id)

    def upsert(self, user_id: str, payload: UserProfileUpsertRequest) -> UserProfile:
        profile = self.repo.get_by_user_id(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id)

        update_data = payload.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            setattr(profile, field_name, value)

        computed = self.bazi_compute_service.build_user_profile_fields(
            birth_date_present=profile.birth_date is not None,
            birth_time_present=profile.birth_time is not None,
        )
        profile.bazi_chart = computed["bazi_chart"]
        profile.five_elements = computed["five_elements"]

        return self.repo.save(profile)
