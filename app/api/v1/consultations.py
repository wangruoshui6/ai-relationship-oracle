import time

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse, success_response
from app.schemas.consultation import ConsultationRequest
from app.services.consultation_service import ConsultationService
from app.utils.sse import chunk_text, sse_event

router = APIRouter(prefix="/consultations", tags=["consultations"])


@router.post("", response_model=ApiResponse)
def create_consultation(
    payload: ConsultationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    result = ConsultationService(db).consult(current_user.id, payload)
    return success_response(result)


@router.post("/stream")
def stream_consultation(
    payload: ConsultationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    def event_stream():
        yield sse_event("status", {"stage": "accepted", "message": "已接收问题，开始分析关系状态..."})
        yield sse_event("status", {"stage": "analyzing", "message": "正在综合八字、心理学、塔罗与关系上下文..."})

        result = ConsultationService(db).consult(current_user.id, payload)
        answer = result.get("answer", "")

        for chunk in chunk_text(answer):
            yield sse_event("delta", {"content": chunk})
            time.sleep(0.02)

        yield sse_event(
            "done",
            {
                "conversation_id": result.get("conversation_id"),
                "partner_id": result.get("partner_id"),
                "answer": answer,
                "structured_result": result.get("structured_result"),
                "auto_created_partner": result.get("auto_created_partner"),
                "memory_updated": result.get("memory_updated"),
                "events_detected": result.get("events_detected"),
                "candidates_created": result.get("candidates_created"),
            },
        )

    return StreamingResponse(event_stream(), media_type="text/event-stream")
