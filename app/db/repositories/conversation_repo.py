from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.conversation_message import ConversationMessage


class ConversationRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_conversation(
        self,
        *,
        user_id: str,
        partner_id: str | None,
        title: str | None,
        conversation_type: str,
        commit: bool = True,
    ) -> Conversation:
        conversation = Conversation(
            user_id=user_id,
            partner_id=partner_id,
            title=title,
            conversation_type=conversation_type,
        )
        self.db.add(conversation)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(conversation)
        return conversation

    def save(self, conversation: Conversation, *, commit: bool = True) -> Conversation:
        self.db.add(conversation)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(conversation)
        return conversation

    def get_by_id_and_user_id(self, conversation_id: str, user_id: str) -> Conversation | None:
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        return self.db.scalar(statement)

    def list_by_user_id(self, user_id: str) -> list[Conversation]:
        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def add_message(
        self,
        *,
        conversation_id: str,
        role: str,
        content: str,
        message_type: str = "text",
        commit: bool = True,
    ) -> ConversationMessage:
        message = ConversationMessage(
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_type=message_type,
        )
        self.db.add(message)
        self.db.flush()
        if commit:
            self.db.commit()
            self.db.refresh(message)
        return message

    def list_messages(self, conversation_id: str) -> list[ConversationMessage]:
        statement = (
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.created_at.asc())
        )
        return list(self.db.scalars(statement).all())
