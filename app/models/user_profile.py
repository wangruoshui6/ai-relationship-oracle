from __future__ import annotations

from datetime import date, time
from typing import Any

from sqlalchemy import Date, ForeignKey, JSON, String, Time, UniqueConstraint
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import CalendarTypeEnum, GenderEnum
from app.db.base_class import Base, TimestampMixin
from app.utils.ids import generate_uuid


class UserProfile(TimestampMixin, Base):
    __tablename__ = "user_profile"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_profile_user_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    gender: Mapped[GenderEnum | None] = mapped_column(
        SqlEnum(
            GenderEnum,
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=True,
    )
    calendar_type: Mapped[CalendarTypeEnum | None] = mapped_column(
        SqlEnum(
            CalendarTypeEnum,
            native_enum=False,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=True,
    )
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    lunar_birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    birth_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    birth_city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    birth_country: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bazi_chart: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    five_elements: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
