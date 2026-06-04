"""Report Service — Week 7. Generates and queries relationship reports."""
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.db.repositories.report_repo import ReportRepo
from app.db.repositories.partner_repo import PartnerProfileRepo
from app.db.repositories.profile_repo import UserProfileRepo
from app.db.repositories.relationship_event_repo import RelationshipEventRepo
from app.db.repositories.relationship_repo import RelationshipRepo
from app.models.report import Report
from app.schemas.report import ReportGenerateRequest
from app.services.report_builder_service import ReportBuilderService


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ReportRepo(db)
        self.builder = ReportBuilderService()
        self.partner_repo = PartnerProfileRepo(db)
        self.profile_repo = UserProfileRepo(db)
        self.event_repo = RelationshipEventRepo(db)
        self.rel_repo = RelationshipRepo(db)

    def generate(self, user_id: str, payload: ReportGenerateRequest) -> Report:
        # Gather context
        context = {}
        context["user_profile"] = self._serialize_user_profile(user_id)
        context["partner"] = self._serialize_partner(user_id, payload.partner_id)
        context["relationship_profile"] = self.rel_repo.get_relationship_profile(user_id, payload.partner_id)
        context["events"] = self.event_repo.list_by_user_partner(user_id, payload.partner_id)
        context["summary"] = self.rel_repo.get_memory_summary(user_id, payload.partner_id)

        # Build report
        report_json = self.builder.build_report(context)
        markdown = self.builder.build_markdown(report_json)

        partner = context["partner"]
        partner_name = partner.get("nickname", "Partner") if partner else "Unknown"
        title = f"Relationship Analysis: {partner_name} - {payload.report_type}"

        report = Report(
            user_id=user_id,
            partner_id=payload.partner_id,
            conversation_id=payload.conversation_id,
            report_type=payload.report_type,
            title=title,
            content_json=report_json,
            content_markdown=markdown,
        )
        return self.repo.save(report)

    def list_reports(self, user_id: str, partner_id: str | None = None) -> list[Report]:
        return self.repo.list_by_user(user_id, partner_id)

    def get_report(self, user_id: str, report_id: str) -> Report:
        report = self.repo.get_by_id_and_user(report_id, user_id)
        if report is None:
            raise AppException(code=1004, message="report not found", status_code=404)
        return report

    def _serialize_user_profile(self, user_id: str) -> dict | None:
        p = self.profile_repo.get_by_user_id(user_id)
        if not p:
            return None
        return {
            "gender": p.gender.value if p.gender else None,
            "birth_date": str(p.birth_date) if p.birth_date else None,
            "birth_time": str(p.birth_time) if p.birth_time else None,
            "bazi_chart": p.bazi_chart,
            "five_elements": p.five_elements,
        }

    def _serialize_partner(self, user_id: str, partner_id: str) -> dict | None:
        p = self.partner_repo.get_by_id_and_user_id(partner_id, user_id)
        if not p:
            return None
        return {
            "nickname": p.nickname,
            "gender": p.gender.value if p.gender else None,
            "birth_date": str(p.birth_date) if p.birth_date else None,
            "bazi_chart": p.bazi_chart,
        }
