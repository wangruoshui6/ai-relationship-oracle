from sqlalchemy.orm import Session

from app.schemas.consultation import ConsultationRequest
from app.schemas.partner_profile import PartnerUpdateRequest
from app.schemas.structured_consultation import StructuredConsultationRequest
from app.services.consultation_service import ConsultationService
from app.services.partner_profile_service import PartnerProfileService
from app.services.user_profile_service import UserProfileService


class StructuredConsultationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.user_profile_service = UserProfileService(db)
        self.partner_profile_service = PartnerProfileService(db)
        self.consultation_service = ConsultationService(db)

    def execute(self, user_id: str, payload: StructuredConsultationRequest) -> dict:
        user_profile = self.user_profile_service.upsert(user_id, payload.user_profile)

        if payload.partner_id:
            partner_profile = self.partner_profile_service.update(
                user_id,
                payload.partner_id,
                PartnerUpdateRequest(**payload.partner_profile.model_dump()),
            )
        else:
            partner_profile = self.partner_profile_service.create(user_id, payload.partner_profile)

        consultation_result = self.consultation_service.consult(
            user_id,
            ConsultationRequest(
                conversation_id=payload.conversation_id,
                partner_id=partner_profile.id,
                message=payload.question,
                analysis_methods=payload.analysis_methods,
            ),
        )

        return {
            "user_profile": user_profile,
            "partner_profile": partner_profile,
            "conversation_id": consultation_result["conversation_id"],
            "partner_id": consultation_result["partner_id"],
            "answer": consultation_result["answer"],
            "structured_result": consultation_result.get("structured_result"),
            "normalized_dates": {
                "user_birth_date": str(user_profile.birth_date) if user_profile.birth_date else None,
                "user_lunar_birth_date": str(user_profile.lunar_birth_date) if user_profile.lunar_birth_date else None,
                "partner_birth_date": str(partner_profile.birth_date) if partner_profile.birth_date else None,
                "partner_lunar_birth_date": str(partner_profile.lunar_birth_date) if partner_profile.lunar_birth_date else None,
            },
            "bazi_ready": {
                "user": bool(user_profile.bazi_chart),
                "partner": bool(partner_profile.bazi_chart),
            },
            "report_generated": consultation_result.get("report_generated", False),
        }
