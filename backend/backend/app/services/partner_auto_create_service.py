from sqlalchemy.orm import Session

from app.schemas.partner_profile import PartnerCreateRequest
from app.services.partner_profile_service import PartnerProfileService


class PartnerAutoCreateService:
    def __init__(self, db: Session) -> None:
        self.partner_service = PartnerProfileService(db)

    def auto_create(self, user_id: str, partner_name: str):
        return self.partner_service.create(
            user_id,
            PartnerCreateRequest(
                nickname=partner_name,
                relationship_type="unknown",
            ),
        )
