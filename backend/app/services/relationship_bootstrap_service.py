from sqlalchemy.orm import Session

from app.core.enums import UpdatedByEnum
from app.db.repositories.relationship_repo import RelationshipRepo
from app.models.memory_summary import MemorySummary
from app.models.relationship_profile import RelationshipProfile


class RelationshipBootstrapService:
    def __init__(self, db: Session) -> None:
        self.repo = RelationshipRepo(db)

    def ensure_bootstrap(
        self,
        *,
        user_id: str,
        partner_id: str,
        current_status: str | None,
        current_goal: str | None,
        partner_name: str,
        commit: bool = True,
    ) -> tuple[RelationshipProfile, MemorySummary, bool]:
        created = False

        relationship_profile = self.repo.get_relationship_profile(user_id, partner_id)
        if relationship_profile is None:
            relationship_profile = RelationshipProfile(
                user_id=user_id,
                partner_id=partner_id,
                current_status=current_status,
                current_goal=current_goal,
                relationship_stage=current_status,
                summary_snapshot=self._build_snapshot(partner_name, current_status, current_goal),
                updated_by=UpdatedByEnum.SYSTEM,
            )
            relationship_profile = self.repo.save_relationship_profile(
                relationship_profile,
                commit=commit,
            )
            created = True

        memory_summary = self.repo.get_memory_summary(user_id, partner_id)
        if memory_summary is None:
            memory_summary = MemorySummary(
                user_id=user_id,
                partner_id=partner_id,
                summary=self._build_summary(partner_name, current_status, current_goal),
                summary_version=1,
            )
            memory_summary = self.repo.save_memory_summary(memory_summary, commit=commit)
            created = True

        return relationship_profile, memory_summary, created

    @staticmethod
    def _build_snapshot(
        partner_name: str,
        current_status: str | None,
        current_goal: str | None,
    ) -> str:
        return (
            f"Relationship target: {partner_name}; "
            f"Current status: {current_status or 'unknown'}; "
            f"Current goal: {current_goal or 'unknown'}"
        )

    @staticmethod
    def _build_summary(
        partner_name: str,
        current_status: str | None,
        current_goal: str | None,
    ) -> str:
        return (
            f"The user is currently consulting about their relationship with {partner_name}. "
            f"The current relationship status is {current_status or 'unknown'}, "
            f"and the current goal is {current_goal or 'unknown'}."
        )
