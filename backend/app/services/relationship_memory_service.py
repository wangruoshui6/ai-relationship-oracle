"""Relationship Memory Service — Week 5.

Aggregates relationship_profile + events + memory_summary for a user-partner pair.
"""
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.db.repositories.relationship_event_repo import RelationshipEventRepo
from app.db.repositories.relationship_repo import RelationshipRepo
from app.models.memory_summary import MemorySummary
from app.models.relationship_event import RelationshipEvent
from app.models.relationship_event_candidate import RelationshipEventCandidate
from app.models.relationship_profile import RelationshipProfile
from app.schemas.relationship_memory_expanded import RelationshipMemoryResponse


class RelationshipMemoryService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.rel_repo = RelationshipRepo(db)
        self.event_repo = RelationshipEventRepo(db)

    def get_memory(self, user_id: str, partner_id: str) -> dict:
        profile = self.rel_repo.get_relationship_profile(user_id, partner_id)
        events = self.event_repo.list_by_user_partner(user_id, partner_id)
        summary = self.rel_repo.get_memory_summary(user_id, partner_id)
        pending = self.event_repo.list_pending_candidates(user_id, partner_id)

        return RelationshipMemoryResponse(
            profile=profile,
            events=events,
            summary=summary,
            candidate_count=len(pending),
        ).model_dump()

    def patch_profile(self, user_id: str, partner_id: str, patch: dict) -> RelationshipProfile:
        from app.core.enums import UpdatedByEnum

        profile = self.rel_repo.get_relationship_profile(user_id, partner_id)
        if profile is None:
            raise AppException(code=1004, message="relationship profile not found", status_code=404)

        updatable_fields = [
            "current_status", "current_goal", "relationship_stage",
            "interaction_pattern", "trust_level", "conflict_level", "intimacy_level",
        ]
        for field in updatable_fields:
            if field in patch and patch[field] is not None:
                setattr(profile, field, patch[field])

        profile.updated_by = UpdatedByEnum.USER
        self.rel_repo.save_relationship_profile(profile)
        return profile
