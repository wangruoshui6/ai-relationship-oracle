from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.schemas.consultation import ConsultationRequest
from app.services.conversation_persistence_service import ConversationPersistenceService
from app.services.conversation_service import ConversationService
from app.services.entity_extraction_service import EntityExtractionService
from app.services.intent_router_service import IntentRouterService
from app.services.llm_provider_service import LLMProviderService
from app.services.partner_auto_create_service import PartnerAutoCreateService
from app.services.prompt_builder_service import PromptBuilderService
from app.services.relationship_bootstrap_service import RelationshipBootstrapService


class ConsultationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.conversation_service = ConversationService(db)
        self.persistence_service = ConversationPersistenceService(db)
        self.prompt_builder = PromptBuilderService()
        self.llm_provider = LLMProviderService()
        self.intent_router = IntentRouterService()
        self.entity_extractor = EntityExtractionService()
        self.partner_auto_create_service = PartnerAutoCreateService(db)
        self.relationship_bootstrap_service = RelationshipBootstrapService(db)

    def consult(self, user_id: str, payload: ConsultationRequest) -> dict:
        intent = self.intent_router.detect_intent(payload.message)
        conversation = self.conversation_service.get_or_create(
            user_id=user_id,
            conversation_id=payload.conversation_id,
            partner_id=payload.partner_id,
            title=self._build_title(payload.message),
            conversation_type=intent,
        )

        auto_created_partner = False
        memory_updated = False
        partner_id = conversation.partner_id

        if intent == "relationship_analysis" and conversation.partner_id is None:
            extraction = self.entity_extractor.extract(payload.message)
            partner_name = extraction.get("partner_name")
            if partner_name:
                partner = self.partner_auto_create_service.auto_create(user_id, partner_name)
                conversation.partner_id = partner.id
                self.conversation_service.repo.save(conversation)
                self.relationship_bootstrap_service.ensure_bootstrap(
                    user_id=user_id,
                    partner_id=partner.id,
                    current_status=extraction.get("current_status"),
                    current_goal=extraction.get("current_goal"),
                    partner_name=partner.nickname,
                )
                partner_id = partner.id
                auto_created_partner = True
                memory_updated = True

        self.persistence_service.save_user_message(conversation.id, payload.message)
        answer = self.llm_provider.generate_text(
            self.prompt_builder.build_consultation_prompt(
                user_message=payload.message,
                analysis_methods=payload.analysis_methods,
                partner_id=partner_id,
            )
        )
        self.persistence_service.save_assistant_message(conversation.id, answer)
        return {
            "conversation_id": conversation.id,
            "partner_id": partner_id,
            "auto_created_partner": auto_created_partner,
            "answer": answer,
            "report_generated": False,
            "memory_updated": memory_updated,
        }

    @staticmethod
    def _build_title(message: str) -> str:
        condensed = message.strip().replace("\n", " ")
        if len(condensed) <= 30:
            return condensed
        return f"{condensed[:30]}..."
