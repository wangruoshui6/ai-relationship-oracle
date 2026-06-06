from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConversationMessageItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    message_type: str
    created_at: datetime


class ConversationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    partner_id: str | None
    title: str | None
    conversation_type: str
    updated_at: datetime


class ConversationDetailResponse(BaseModel):
    id: str
    partner_id: str | None
    title: str | None
    conversation_type: str
    created_at: datetime
    updated_at: datetime
    messages: list[ConversationMessageItem]
