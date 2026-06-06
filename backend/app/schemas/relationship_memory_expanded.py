"""Week 5 schemas: relationship_memory expanded."""
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import UpdatedByEnum


# --- Relationship Profile ---
class RelationshipProfilePatchRequest(BaseModel):
    current_status: str | None = Field(default=None, max_length=64)
    current_goal: str | None = Field(default=None, max_length=64)
    relationship_stage: str | None = Field(default=None, max_length=64)
    interaction_pattern: str | None = Field(default=None, max_length=128)
    trust_level: str | None = Field(default=None, max_length=64)
    conflict_level: str | None = Field(default=None, max_length=64)
    intimacy_level: str | None = Field(default=None, max_length=64)
    updated_by: UpdatedByEnum = UpdatedByEnum.USER


# --- Relationship Events ---
class RelationshipEventItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: str
    event_date: date | None
    description: str
    source: str
    confidence_score: float
    created_at: datetime


# --- Event Candidates ---
class EventCandidateItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: str
    event_date: date | None
    description: str
    confidence_score: float
    candidate_status: str
    created_at: datetime


# --- Aggregated Memory Response ---
class RelationshipMemoryResponse(BaseModel):
    profile: "RelationshipProfileSnapshot | None"
    events: list[RelationshipEventItem]
    summary: "MemorySummaryData | None"
    candidate_count: int


# Late imports for forward refs
from app.schemas.relationship_memory import MemorySummaryData, RelationshipProfileSnapshot
RelationshipMemoryResponse.model_rebuild()
EventCandidateItem.model_rebuild()
