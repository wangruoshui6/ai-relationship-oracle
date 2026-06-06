"""EvaluationCase ORM model — Week 8."""
from __future__ import annotations
from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base, TimestampMixin
from app.utils.ids import generate_uuid

class EvaluationCase(TimestampMixin, Base):
    __tablename__ = "evaluation_case"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    case_name: Mapped[str] = mapped_column(String(255), nullable=False)
    case_type: Mapped[str] = mapped_column(String(64), nullable=False)
    input_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    expected_rules: Mapped[dict] = mapped_column(JSON, nullable=False)
