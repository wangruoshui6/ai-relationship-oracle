from sqlalchemy.orm import Session

from app.db.repositories.profile_repo import UserProfileRepo
from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileUpsertRequest
from app.services.bazi_profile_compute_service import BaziProfileComputeService
from app.services.date_normalization_service import DateNormalizationService


class UserProfileService:
    def __init__(self, db: Session) -> None:
        self.repo = UserProfileRepo(db)
        self.bazi_compute_service = BaziProfileComputeService()
        self.date_normalization_service = DateNormalizationService()

    def get_by_user_id(self, user_id: str) -> UserProfile | None:
        return self.repo.get_by_user_id(user_id)

    def upsert(self, user_id: str, payload: UserProfileUpsertRequest) -> UserProfile:
        profile = self.repo.get_by_user_id(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id)

        update_data = payload.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            setattr(profile, field_name, value)

        normalized_birth_date, lunar_birth_date = self.date_normalization_service.normalize_birth_date(
            birth_date=profile.birth_date,
            calendar_type=profile.calendar_type,
            is_leap_month=payload.is_leap_month,
        )
        profile.birth_date = normalized_birth_date
        profile.lunar_birth_date = lunar_birth_date

        # Compute real Bazi chart with actual birth date/time
        computed = self.bazi_compute_service.build_user_profile_fields(
            birth_date_present=profile.birth_date is not None,
            birth_time_present=profile.birth_time is not None,
            birth_date=profile.birth_date,
            birth_time=profile.birth_time,
        )
        profile.bazi_chart = computed["bazi_chart"]
        profile.five_elements = computed["five_elements"]

        return self.repo.save(profile)
