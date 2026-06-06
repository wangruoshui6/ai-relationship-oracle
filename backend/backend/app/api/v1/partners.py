from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse, success_response
from app.schemas.partner_profile import (
    PartnerCreateRequest,
    PartnerDetailResponse,
    PartnerListItem,
    PartnerUpdateRequest,
)
from app.services.partner_profile_service import PartnerProfileService

router = APIRouter(prefix="/partners", tags=["partners"])


@router.get("", response_model=ApiResponse)
def list_partners(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    partners = PartnerProfileService(db).list_by_user_id(current_user.id)
    items = [PartnerListItem.model_validate(item).model_dump() for item in partners]
    return success_response(items)


@router.post("", response_model=ApiResponse)
def create_partner(
    payload: PartnerCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    partner = PartnerProfileService(db).create(current_user.id, payload)
    return success_response(PartnerDetailResponse.model_validate(partner).model_dump())


@router.get("/{partner_id}", response_model=ApiResponse)
def get_partner(
    partner_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    partner = PartnerProfileService(db).get_or_raise(current_user.id, partner_id)
    return success_response(PartnerDetailResponse.model_validate(partner).model_dump())


@router.put("/{partner_id}", response_model=ApiResponse)
def update_partner(
    partner_id: str,
    payload: PartnerUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    partner = PartnerProfileService(db).update(current_user.id, partner_id, payload)
    return success_response(PartnerDetailResponse.model_validate(partner).model_dump())


@router.delete("/{partner_id}", response_model=ApiResponse)
def delete_partner(
    partner_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    PartnerProfileService(db).delete(current_user.id, partner_id)
    return success_response({"deleted": True})
