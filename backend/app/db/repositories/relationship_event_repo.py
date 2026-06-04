"""Repository for relationship events and candidates — Week 5."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.relationship_event import RelationshipEvent
from app.models.relationship_event_candidate import RelationshipEventCandidate


class RelationshipEventRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_by_user_partner(self, user_id: str, partner_id: str) -> list[RelationshipEvent]:
        stmt = (
            select(RelationshipEvent)
            .where(
                RelationshipEvent.user_id == user_id,
                RelationshipEvent.partner_id == partner_id,
            )
            .order_by(RelationshipEvent.event_date.desc().nullslast(), RelationshipEvent.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def save_event(self, event: RelationshipEvent) -> RelationshipEvent:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    # --- Candidates ---
    def list_pending_candidates(self, user_id: str, partner_id: str) -> list[RelationshipEventCandidate]:
        stmt = (
            select(RelationshipEventCandidate)
            .where(
                RelationshipEventCandidate.user_id == user_id,
                RelationshipEventCandidate.partner_id == partner_id,
                RelationshipEventCandidate.candidate_status == "pending",
            )
            .order_by(RelationshipEventCandidate.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_candidate(self, candidate_id: str) -> RelationshipEventCandidate | None:
        return self.db.scalar(
            select(RelationshipEventCandidate).where(
                RelationshipEventCandidate.id == candidate_id
            )
        )

    def save_candidate(self, candidate: RelationshipEventCandidate) -> RelationshipEventCandidate:
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate
