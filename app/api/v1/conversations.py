from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse, success_response
from app.schemas.conversation import (
    ConversationDetailResponse,
    ConversationListItem,
    ConversationMessageItem,
)
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=ApiResponse)
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    conversations = ConversationService(db).list_conversations(current_user.id)
    items = [ConversationListItem.model_validate(item).model_dump() for item in conversations]
    return success_response(items)


@router.get("/{conversation_id}", response_model=ApiResponse)
def get_conversation_detail(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    conversation, messages = ConversationService(db).get_detail(current_user.id, conversation_id)
    response = ConversationDetailResponse(
        id=conversation.id,
        partner_id=conversation.partner_id,
        title=conversation.title,
        conversation_type=conversation.conversation_type,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[ConversationMessageItem.model_validate(message) for message in messages],
    )
    return success_response(response.model_dump())
