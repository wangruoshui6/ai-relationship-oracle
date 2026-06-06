from __future__ import annotations

from sqlalchemy import ForeignKey, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin
from app.utils.ids import generate_uuid


class ConversationType(str):
    RELATIONSHIP_ANALYSIS = "relationship_analysis"
    EMOTIONAL_SUPPORT = "emotional_support"
    GENERAL_GUIDANCE = "general_guidance"


class Conversation(TimestampMixin, Base):
    __tablename__ = "conversation"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    partner_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("partner_profile.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    conversation_type: Mapped[str] = mapped_column(
        String(64),
        default="relationship_analysis",
        nullable=False,
    )
