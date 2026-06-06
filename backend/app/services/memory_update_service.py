"""Memory Update Service — Week 5.

Handles event candidate confirmation/rejection and memory re-computation.
"""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.db.repositories.relationship_event_repo import RelationshipEventRepo
from app.models.relationship_event import RelationshipEvent
from app.models.relationship_event_candidate import RelationshipEventCandidate
from app.utils.ids import generate_uuid


class MemoryUpdateService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.event_repo = RelationshipEventRepo(db)

    def confirm_candidate(self, candidate_id: str, user_id: str) -> RelationshipEvent:
        candidate = self._get_and_validate(candidate_id, user_id)

        event = RelationshipEvent(
            id=generate_uuid(),
            user_id=candidate.user_id,
            partner_id=candidate.partner_id,
            event_type=candidate.event_type,
            event_date=candidate.event_date,
            description=candidate.description,
            source="confirmed",
            confidence_score=1.0,
        )
        self.event_repo.save_event(event)

        candidate.candidate_status = "confirmed"
        candidate.confirmed_at = datetime.now(timezone.utc)
        self.event_repo.save_candidate(candidate)

        return event

    def reject_candidate(self, candidate_id: str, user_id: str) -> RelationshipEventCandidate:
        candidate = self._get_and_validate(candidate_id, user_id)
        candidate.candidate_status = "rejected"
        candidate.confirmed_at = datetime.now(timezone.utc)
        return self.event_repo.save_candidate(candidate)

    def _get_and_validate(self, candidate_id: str, user_id: str) -> RelationshipEventCandidate:
        candidate = self.event_repo.get_candidate(candidate_id)
        if candidate is None:
            raise AppException(code=1004, message="candidate not found", status_code=404)
        if candidate.user_id != user_id:
            raise AppException(code=1002, message="unauthorized", status_code=401)
        if candidate.candidate_status != "pending":
            raise AppException(code=1006, message="candidate already processed", status_code=400)
        return candidate
