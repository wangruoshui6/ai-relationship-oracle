"""EvaluationRun ORM model — Week 8."""
from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, Float, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base_class import Base
from app.utils.ids import generate_uuid

class EvaluationRun(Base):
    __tablename__ = "evaluation_run"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    run_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_name: Mapped[str] = mapped_column(String(128), default="deepseek-chat")
    prompt_version: Mapped[str] = mapped_column(String(32), default="v1")
    workflow_version: Mapped[str] = mapped_column(String(32), default="v1")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="running")
    total_cases: Mapped[int] = mapped_column(Integer, default=0)
    passed_cases: Mapped[int] = mapped_column(Integer, default=0)
    pass_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
