"""EvaluationResult ORM model — Week 8."""
from __future__ import annotations
from sqlalchemy import Boolean, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base, TimestampMixin
from app.utils.ids import generate_uuid

class EvaluationResult(TimestampMixin, Base):
    __tablename__ = "evaluation_result"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(String(36), ForeignKey("evaluation_run.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id: Mapped[str] = mapped_column(String(36), ForeignKey("evaluation_case.id", ondelete="CASCADE"), nullable=False)
    score_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    llm_judge_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
