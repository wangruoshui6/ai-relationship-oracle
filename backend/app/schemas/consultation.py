from pydantic import BaseModel, Field


class ConsultationRequest(BaseModel):
    conversation_id: str | None = None
    partner_id: str | None = None
    message: str = Field(min_length=1)
    analysis_methods: list[str] | None = None


class ConsultationResponse(BaseModel):
    conversation_id: str
    partner_id: str | None
    auto_created_partner: bool = False
    answer: str
    report_generated: bool = False
