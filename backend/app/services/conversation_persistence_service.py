from sqlalchemy.orm import Session

from app.db.repositories.conversation_repo import ConversationRepo


class ConversationPersistenceService:
    def __init__(self, db: Session) -> None:
        self.repo = ConversationRepo(db)

    def save_user_message(self, conversation_id: str, content: str) -> None:
        self.repo.add_message(
            conversation_id=conversation_id,
            role="user",
            content=content,
        )

    def save_assistant_message(self, conversation_id: str, content: str) -> None:
        self.repo.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=content,
        )
