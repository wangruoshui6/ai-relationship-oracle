from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin
from app.utils.ids import generate_uuid


class MemorySummary(TimestampMixin, Base):
    __tablename__ = "memory_summary"
    __table_args__ = (
        UniqueConstraint("user_id", "partner_id", name="uq_memory_summary_user_partner"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    partner_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("partner_profile.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    summary_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
