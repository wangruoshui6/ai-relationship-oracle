"""Repository for reports — Week 7."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.report import Report


class ReportRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save(self, report: Report) -> Report:
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def list_by_user(self, user_id: str, partner_id: str | None = None) -> list[Report]:
        stmt = select(Report).where(Report.user_id == user_id)
        if partner_id:
            stmt = stmt.where(Report.partner_id == partner_id)
        stmt = stmt.order_by(Report.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id_and_user(self, report_id: str, user_id: str) -> Report | None:
        return self.db.scalar(
            select(Report).where(Report.id == report_id, Report.user_id == user_id)
        )
