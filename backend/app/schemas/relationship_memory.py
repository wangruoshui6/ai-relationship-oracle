from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.core.enums import UpdatedByEnum


class RelationshipProfileSnapshot(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    partner_id: str
    current_status: str | None
    current_goal: str | None
    relationship_stage: str | None
    interaction_pattern: str | None
    trust_level: str | None
    conflict_level: str | None
    intimacy_level: str | None
    last_major_event: str | None
    summary_snapshot: str | None
    updated_by: UpdatedByEnum
    created_at: datetime
    updated_at: datetime


class MemorySummaryData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    partner_id: str
    summary: str
    summary_version: int
    created_at: datetime
    updated_at: datetime
