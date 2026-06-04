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
            relationship_profile = self.repo.save_relationship_profile(relationship_profile)
            created = True

        memory_summary = self.repo.get_memory_summary(user_id, partner_id)
        if memory_summary is None:
            memory_summary = MemorySummary(
                user_id=user_id,
                partner_id=partner_id,
                summary=self._build_summary(partner_name, current_status, current_goal),
                summary_version=1,
            )
            memory_summary = self.repo.save_memory_summary(memory_summary)
            created = True

        return relationship_profile, memory_summary, created

    @staticmethod
    def _build_snapshot(
        partner_name: str,
        current_status: str | None,
        current_goal: str | None,
    ) -> str:
        return (
            f"关系对象: {partner_name}; "
            f"当前状态: {current_status or 'unknown'}; "
            f"当前目标: {current_goal or 'unknown'}"
        )

    @staticmethod
    def _build_summary(
        partner_name: str,
        current_status: str | None,
        current_goal: str | None,
    ) -> str:
        return (
            f"用户当前正在咨询与 {partner_name} 的关系。"
            f"当前关系状态为 {current_status or 'unknown'}，"
            f"当前目标为 {current_goal or 'unknown'}。"
        )
