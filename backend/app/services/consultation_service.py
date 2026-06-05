from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.db.repositories.partner_repo import PartnerProfileRepo
from app.db.repositories.profile_repo import UserProfileRepo
from app.db.repositories.relationship_event_repo import RelationshipEventRepo
from app.db.repositories.relationship_repo import RelationshipRepo
from app.schemas.consultation import ConsultationRequest
from app.services.compatibility_engine_service import CompatibilityEngineService
from app.services.conversation_persistence_service import ConversationPersistenceService
from app.services.conversation_service import ConversationService
from app.services.entity_extraction_service import EntityExtractionService
from app.services.event_detector_service import EventDetectorService
from app.services.intent_router_service import IntentRouterService
from app.services.llm_provider_service import LLMProviderService
from app.services.partner_auto_create_service import PartnerAutoCreateService
from app.services.prompt_builder_service import PromptBuilderService
from app.services.redis_context_service import redis_context
from app.services.relationship_bootstrap_service import RelationshipBootstrapService
from app.services.tool_router_service import ToolRouterService


class ConsultationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.conversation_service = ConversationService(db)
        self.persistence_service = ConversationPersistenceService(db)
        self.prompt_builder = PromptBuilderService()
        self.llm_provider = LLMProviderService()
        self.intent_router = IntentRouterService()
        self.entity_extractor = EntityExtractionService()
        self.event_detector = EventDetectorService()
        self.tool_router = ToolRouterService()
        self.compatibility_engine = CompatibilityEngineService()
        self.partner_auto_create_service = PartnerAutoCreateService(db)
        self.relationship_bootstrap_service = RelationshipBootstrapService(db)
        self.event_repo = RelationshipEventRepo(db)
        self.rel_repo = RelationshipRepo(db)
        self.user_profile_repo = UserProfileRepo(db)
        self.partner_repo = PartnerProfileRepo(db)

    def consult(self, user_id: str, payload: ConsultationRequest) -> dict:
        intent = self.intent_router.detect_intent(payload.message)
        conversation = self.conversation_service.get_or_create(
            user_id=user_id,
            conversation_id=payload.conversation_id,
            partner_id=payload.partner_id,
            title=self._build_title(payload.message),
            conversation_type=intent,
            commit=False,
        )

        # Always preserve the user message first so the conversation has an audit trail
        # even if deeper analysis fails later.
        self.persistence_service.save_user_message(conversation.id, payload.message, commit=False)
        self.db.commit()
        redis_context.append(conversation.id, "user", payload.message)

        auto_created_partner = False
        memory_updated = False
        events_detected = 0
        candidates_created = 0
        partner_id = conversation.partner_id
        structured_result = None

        try:
            if intent == "relationship_analysis" and conversation.partner_id is None:
                extraction = self.entity_extractor.extract(payload.message)
                partner_name = extraction.get("partner_name")
                if partner_name:
                    partner = self.partner_auto_create_service.auto_create(user_id, partner_name)
                    conversation.partner_id = partner.id
                    self.conversation_service.repo.save(conversation, commit=False)
                    self.relationship_bootstrap_service.ensure_bootstrap(
                        user_id=user_id,
                        partner_id=partner.id,
                        current_status=extraction.get("current_status"),
                        current_goal=extraction.get("current_goal"),
                        partner_name=partner.nickname,
                        commit=False,
                    )
                    partner_id = partner.id
                    auto_created_partner = True
                    memory_updated = True

            if partner_id:
                events, candidates = self.event_detector.detect(user_id, partner_id, payload.message)
                for event in events:
                    self.event_repo.save_event(event, commit=False)
                    events_detected += 1
                for candidate in candidates:
                    self.event_repo.save_candidate(candidate, commit=False)
                    candidates_created += 1

            methods = self.tool_router.validate_methods(payload.analysis_methods)
            memory_context = self._load_memory_context(user_id, partner_id)
            tool_data = self._collect_tool_data(user_id, partner_id)
            tool_data["user_message"] = payload.message
            structured_result = self.tool_router.run_all(methods, tool_data)

            bazi_tr = next((tr for tr in structured_result.tool_results if tr.tool == "bazi"), None)
            psych_tr = next((tr for tr in structured_result.tool_results if tr.tool == "psychology"), None)
            tarot_tr = next((tr for tr in structured_result.tool_results if tr.tool == "tarot"), None)
            compatibility_result = self.compatibility_engine.synthesize(
                bazi_tr,
                psych_tr,
                tarot_tr,
                memory_context,
            )
            structured_result.tool_results.append(compatibility_result)

            system_prompt = self.prompt_builder.build_system_prompt(memory_context, structured_result)
            user_prompt = self.prompt_builder.build_consultation_prompt(
                user_message=payload.message,
                analysis_methods=payload.analysis_methods,
                partner_id=partner_id,
                memory_context=memory_context,
            )
            answer = self.llm_provider.generate_text(system_prompt, user_prompt)

            self.persistence_service.save_assistant_message(conversation.id, answer, commit=False)
            self.db.commit()
            redis_context.append(conversation.id, "assistant", answer)
        except AppException:
            self.db.rollback()
            answer = (
                "I can continue helping with this relationship question, but the deeper analysis "
                "step ran into a temporary issue just now. You can retry in a moment, or tell me "
                "a little more about the relationship context and I will continue with a lighter answer."
            )
            self.persistence_service.save_assistant_message(conversation.id, answer)
            redis_context.append(conversation.id, "assistant", answer)

        return {
            "conversation_id": conversation.id,
            "partner_id": partner_id,
            "auto_created_partner": auto_created_partner,
            "answer": answer,
            "report_generated": False,
            "memory_updated": memory_updated,
            "events_detected": events_detected,
            "candidates_created": candidates_created,
            "structured_result": structured_result.model_dump() if structured_result else None,
        }

    def _collect_tool_data(self, user_id: str, partner_id: str | None) -> dict:
        data: dict = {}
        user_profile = self.user_profile_repo.get_by_user_id(user_id)
        if user_profile:
            if user_profile.bazi_chart:
                data["bazi_chart"] = user_profile.bazi_chart
            if user_profile.five_elements:
                data["five_elements"] = user_profile.five_elements
            if user_profile.gender:
                data["gender"] = user_profile.gender.value
        if partner_id:
            partner = self.partner_repo.get_by_id_and_user_id(partner_id, user_id)
            if partner and partner.bazi_chart:
                data["partner_bazi_chart"] = partner.bazi_chart
                if partner.bazi_chart.get("zodiac"):
                    data["partner_zodiac"] = partner.bazi_chart["zodiac"]
            profile = self.rel_repo.get_relationship_profile(user_id, partner_id)
            if profile:
                data["current_status"] = profile.current_status
                data["conflict_level"] = profile.conflict_level
                data["trust_level"] = profile.trust_level
                data["intimacy_level"] = profile.intimacy_level
        return data

    def _load_memory_context(self, user_id: str, partner_id: str | None) -> dict | None:
        if not partner_id:
            return None
        profile = self.rel_repo.get_relationship_profile(user_id, partner_id)
        summary = self.rel_repo.get_memory_summary(user_id, partner_id)
        events = self.event_repo.list_by_user_partner(user_id, partner_id)
        return {"profile": profile, "summary": summary, "recent_events": events[:5]}

    @staticmethod
    def _build_title(message: str) -> str:
        condensed = message.strip().replace("\n", " ")
        return condensed if len(condensed) <= 30 else f"{condensed[:30]}..."
