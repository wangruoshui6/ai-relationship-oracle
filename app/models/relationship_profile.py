from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import UpdatedByEnum
from app.db.base_class import Base, TimestampMixin
from app.utils.ids import generate_uuid


class RelationshipProfile(TimestampMixin, Base):
    __tablename__ = "relationship_profile"
    __table_args__ = (
        UniqueConstraint("user_id", "partner_id", name="uq_relationship_profile_user_partner"),
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
    current_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    current_goal: Mapped[str | None] = mapped_column(String(64), nullable=True)
    relationship_stage: Mapped[str | None] = mapped_column(String(64), nullable=True)
    interaction_pattern: Mapped[str | None] = mapped_column(String(128), nullable=True)
    trust_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    conflict_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    intimacy_level: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_major_event: Mapped[str | None] = mapped_column(String(128), nullable=True)
    summary_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_by: Mapped[UpdatedByEnum] = mapped_column(
        SqlEnum(
            UpdatedByEnum,
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=UpdatedByEnum.SYSTEM,
        nullable=False,
    )
