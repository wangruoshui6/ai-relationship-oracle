from datetime import date, datetime, time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import GenderEnum, RelationshipTypeEnum


class PartnerCreateRequest(BaseModel):
    nickname: str = Field(min_length=1, max_length=255)
    gender: GenderEnum | None = None
    relationship_type: RelationshipTypeEnum | None = None
    birth_date: date | None = None
    birth_time: time | None = None
    birth_city: str | None = None
    birth_country: str | None = None


class PartnerUpdateRequest(BaseModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=255)
    gender: GenderEnum | None = None
    relationship_type: RelationshipTypeEnum | None = None
    birth_date: date | None = None
    birth_time: time | None = None
    birth_city: str | None = None
    birth_country: str | None = None


class PartnerListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nickname: str
    gender: GenderEnum | None
    relationship_type: RelationshipTypeEnum | None
    updated_at: datetime


class PartnerDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    nickname: str
    gender: GenderEnum | None
    relationship_type: RelationshipTypeEnum | None
    birth_date: date | None
    birth_time: time | None
    birth_city: str | None
    birth_country: str | None
    bazi_chart: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
