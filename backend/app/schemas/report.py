"""Week 7: Report schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReportGenerateRequest(BaseModel):
    partner_id: str = Field(...)
    report_type: str = Field(default="relationship_analysis")
    conversation_id: str | None = Field(default=None)


class ReportListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    partner_id: str | None
    report_type: str
    title: str
    created_at: datetime


class ReportDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    partner_id: str | None
    conversation_id: str | None
    report_type: str
    title: str
    content_json: dict | None
    content_markdown: str | None
    created_at: datetime
    updated_at: datetime
