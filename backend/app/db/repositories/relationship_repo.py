from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.memory_summary import MemorySummary
from app.models.relationship_profile import RelationshipProfile


class RelationshipRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_relationship_profile(
        self, user_id: str, partner_id: str
    ) -> RelationshipProfile | None:
        statement = select(RelationshipProfile).where(
            RelationshipProfile.user_id == user_id,
            RelationshipProfile.partner_id == partner_id,
        )
        return self.db.scalar(statement)

    def save_relationship_profile(
        self, relationship_profile: RelationshipProfile
    ) -> RelationshipProfile:
        self.db.add(relationship_profile)
        self.db.commit()
        self.db.refresh(relationship_profile)
        return relationship_profile

    def get_memory_summary(self, user_id: str, partner_id: str) -> MemorySummary | None:
        statement = select(MemorySummary).where(
            MemorySummary.user_id == user_id,
            MemorySummary.partner_id == partner_id,
        )
        return self.db.scalar(statement)

    def save_memory_summary(self, memory_summary: MemorySummary) -> MemorySummary:
        self.db.add(memory_summary)
        self.db.commit()
        self.db.refresh(memory_summary)
        return memory_summary
