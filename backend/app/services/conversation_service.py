from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.db.repositories.conversation_repo import ConversationRepo
from app.models.conversation import Conversation


class ConversationService:
    def __init__(self, db: Session) -> None:
        self.repo = ConversationRepo(db)

    def get_or_create(
        self,
        *,
        user_id: str,
        conversation_id: str | None,
        partner_id: str | None,
        title: str | None,
        conversation_type: str,
    ) -> Conversation:
        if conversation_id:
            conversation = self.repo.get_by_id_and_user_id(conversation_id, user_id)
            if conversation is None:
                raise AppException(code=1004, message="conversation not found", status_code=404)
            return conversation

        return self.repo.create_conversation(
            user_id=user_id,
            partner_id=partner_id,
            title=title,
            conversation_type=conversation_type,
        )

    def list_conversations(self, user_id: str) -> list[Conversation]:
        return self.repo.list_by_user_id(user_id)

    def get_detail(self, user_id: str, conversation_id: str) -> tuple[Conversation, list]:
        conversation = self.repo.get_by_id_and_user_id(conversation_id, user_id)
        if conversation is None:
            raise AppException(code=1004, message="conversation not found", status_code=404)
        messages = self.repo.list_messages(conversation_id)
        return conversation, messages
