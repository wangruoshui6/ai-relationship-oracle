from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.partner_profile import PartnerProfile


class PartnerProfileRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_user_id(self, user_id: str) -> list[PartnerProfile]:
        statement = (
            select(PartnerProfile)
            .where(PartnerProfile.user_id == user_id)
            .order_by(PartnerProfile.updated_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def get_by_id_and_user_id(self, partner_id: str, user_id: str) -> PartnerProfile | None:
        statement = select(PartnerProfile).where(
            PartnerProfile.id == partner_id,
            PartnerProfile.user_id == user_id,
        )
        return self.db.scalar(statement)

    def save(self, partner: PartnerProfile) -> PartnerProfile:
        self.db.add(partner)
        self.db.commit()
        self.db.refresh(partner)
        return partner

    def delete(self, partner: PartnerProfile) -> None:
        self.db.delete(partner)
        self.db.commit()
