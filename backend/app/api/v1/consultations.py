from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse, success_response
from app.schemas.consultation import ConsultationRequest
from app.services.consultation_service import ConsultationService

router = APIRouter(prefix="/consultations", tags=["consultations"])


@router.post("", response_model=ApiResponse)
def create_consultation(
    payload: ConsultationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    result = ConsultationService(db).consult(current_user.id, payload)
    return success_response(result)
