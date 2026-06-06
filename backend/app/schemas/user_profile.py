from datetime import date, datetime, time
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.core.enums import CalendarTypeEnum, GenderEnum


class UserProfileUpsertRequest(BaseModel):
    name: str | None = None
    gender: GenderEnum | None = None
    birth_date: date | None = None
    birth_time: time | None = None
    birth_city: str | None = None
    birth_country: str | None = None
    calendar_type: CalendarTypeEnum = CalendarTypeEnum.SOLAR
    is_leap_month: bool = False


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str | None
    gender: GenderEnum | None
    calendar_type: CalendarTypeEnum | None
    birth_date: date | None
    lunar_birth_date: date | None
    birth_time: time | None
    birth_city: str | None
    birth_country: str | None
    bazi_chart: dict[str, Any] | None
    five_elements: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
