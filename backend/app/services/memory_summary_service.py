from sqlalchemy.orm import Session

from app.db.repositories.relationship_repo import RelationshipRepo
from app.models.memory_summary import MemorySummary


class MemorySummaryService:
    def __init__(self, db: Session) -> None:
        self.repo = RelationshipRepo(db)

    def get_by_user_partner(self, user_id: str, partner_id: str) -> MemorySummary | None:
        return self.repo.get_memory_summary(user_id, partner_id)
