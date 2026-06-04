from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.schemas.consultation import ConsultationRequest
from app.services.conversation_persistence_service import ConversationPersistenceService
from app.services.conversation_service import ConversationService
from app.services.llm_provider_service import LLMProviderService
from app.services.prompt_builder_service import PromptBuilderService


class ConsultationService:
    def __init__(self, db: Session) -> None:
        self.conversation_service = ConversationService(db)
        self.persistence_service = ConversationPersistenceService(db)
        self.prompt_builder = PromptBuilderService()
        self.llm_provider = LLMProviderService()

    def consult(self, user_id: str, payload: ConsultationRequest) -> dict:
        conversation = self.conversation_service.get_or_create(
            user_id=user_id,
            conversation_id=payload.conversation_id,
            partner_id=payload.partner_id,
            title=self._build_title(payload.message),
            conversation_type="relationship_analysis",
        )
        self.persistence_service.save_user_message(conversation.id, payload.message)
        answer = self.llm_provider.generate_text(
            self.prompt_builder.build_consultation_prompt(
                user_message=payload.message,
                analysis_methods=payload.analysis_methods,
                partner_id=conversation.partner_id,
            )
        )
        self.persistence_service.save_assistant_message(conversation.id, answer)
        return {
            "conversation_id": conversation.id,
            "partner_id": conversation.partner_id,
            "auto_created_partner": False,
            "answer": answer,
            "report_generated": False,
        }

    @staticmethod
    def _build_title(message: str) -> str:
        condensed = message.strip().replace("\n", " ")
        if len(condensed) <= 30:
            return condensed
        return f"{condensed[:30]}..."
