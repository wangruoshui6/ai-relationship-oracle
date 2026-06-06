from pydantic import BaseModel, Field

from app.schemas.partner_profile import PartnerCreateRequest, PartnerDetailResponse
from app.schemas.user_profile import UserProfileResponse, UserProfileUpsertRequest


class StructuredConsultationRequest(BaseModel):
    conversation_id: str | None = None
    partner_id: str | None = None
    user_profile: UserProfileUpsertRequest
    partner_profile: PartnerCreateRequest
    question: str = Field(min_length=1)
    analysis_methods: list[str] | None = None


class StructuredConsultationResponse(BaseModel):
    user_profile: UserProfileResponse
    partner_profile: PartnerDetailResponse
    conversation_id: str
    partner_id: str
    answer: str
    structured_result: dict | None = None
    normalized_dates: dict
    bazi_ready: dict
    report_generated: bool = False
