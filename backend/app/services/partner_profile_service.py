from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.db.repositories.partner_repo import PartnerProfileRepo
from app.models.partner_profile import PartnerProfile
from app.schemas.partner_profile import PartnerCreateRequest, PartnerUpdateRequest
from app.services.bazi_profile_compute_service import BaziProfileComputeService


class PartnerProfileService:
    def __init__(self, db: Session) -> None:
        self.repo = PartnerProfileRepo(db)
        self.bazi_compute_service = BaziProfileComputeService()

    def list_by_user_id(self, user_id: str) -> list[PartnerProfile]:
        return self.repo.list_by_user_id(user_id)

    def create(self, user_id: str, payload: PartnerCreateRequest) -> PartnerProfile:
        partner = PartnerProfile(
            user_id=user_id,
            **payload.model_dump(),
        )
        self._apply_bazi_chart(partner)
        return self.repo.save(partner)

    def get_or_raise(self, user_id: str, partner_id: str) -> PartnerProfile:
        partner = self.repo.get_by_id_and_user_id(partner_id, user_id)
        if partner is None:
            raise AppException(code=1004, message="partner not found", status_code=404)
        return partner

    def update(
        self,
        user_id: str,
        partner_id: str,
        payload: PartnerUpdateRequest,
    ) -> PartnerProfile:
        partner = self.get_or_raise(user_id, partner_id)
        update_data = payload.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            setattr(partner, field_name, value)
        self._apply_bazi_chart(partner)
        return self.repo.save(partner)

    def delete(self, user_id: str, partner_id: str) -> None:
        partner = self.get_or_raise(user_id, partner_id)
        self.repo.delete(partner)

    def _apply_bazi_chart(self, partner: PartnerProfile) -> None:
        computed = self.bazi_compute_service.build_partner_profile_fields(
            birth_date_present=partner.birth_date is not None,
            birth_time_present=partner.birth_time is not None,
        )
        partner.bazi_chart = computed["bazi_chart"]
