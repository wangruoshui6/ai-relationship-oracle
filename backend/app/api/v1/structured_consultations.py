import time

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse, success_response
from app.schemas.partner_profile import PartnerDetailResponse
from app.schemas.structured_consultation import StructuredConsultationRequest
from app.schemas.user_profile import UserProfileResponse
from app.services.structured_consultation_service import StructuredConsultationService
from app.utils.sse import chunk_text, sse_event

router = APIRouter(prefix="/structured-consultations", tags=["structured-consultations"])


@router.post("", response_model=ApiResponse)
def create_structured_consultation(
    payload: StructuredConsultationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    result = StructuredConsultationService(db).execute(current_user.id, payload)
    data = {
        "user_profile": UserProfileResponse.model_validate(result["user_profile"]).model_dump(),
        "partner_profile": PartnerDetailResponse.model_validate(result["partner_profile"]).model_dump(),
        "conversation_id": result["conversation_id"],
        "partner_id": result["partner_id"],
        "answer": result["answer"],
        "structured_result": result["structured_result"],
        "normalized_dates": result["normalized_dates"],
        "bazi_ready": result["bazi_ready"],
        "report_generated": result["report_generated"],
    }
    return success_response(data)


@router.post("/stream")
def stream_structured_consultation(
    payload: StructuredConsultationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    def event_stream():
        yield sse_event("status", {"stage": "profile", "message": "正在整理双方资料..."})
        yield sse_event("status", {"stage": "calendar", "message": "正在归一化农历/公历并计算八字..."})
        yield sse_event("status", {"stage": "consult", "message": "正在生成情感分析回答..."})

        result = StructuredConsultationService(db).execute(current_user.id, payload)
        answer = result.get("answer", "")

        for chunk in chunk_text(answer):
            yield sse_event("delta", {"content": chunk})
            time.sleep(0.02)

        yield sse_event(
            "done",
            {
                "user_profile": UserProfileResponse.model_validate(result["user_profile"]).model_dump(),
                "partner_profile": PartnerDetailResponse.model_validate(result["partner_profile"]).model_dump(),
                "conversation_id": result["conversation_id"],
                "partner_id": result["partner_id"],
                "answer": answer,
                "structured_result": result.get("structured_result"),
                "normalized_dates": result["normalized_dates"],
                "bazi_ready": result["bazi_ready"],
                "report_generated": result.get("report_generated", False),
            },
        )

    return StreamingResponse(event_stream(), media_type="text/event-stream")
