from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse, success_response
from app.schemas.user_profile import UserProfileResponse, UserProfileUpsertRequest
from app.services.user_profile_service import UserProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("/me", response_model=ApiResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    profile = UserProfileService(db).get_by_user_id(current_user.id)
    if profile is None:
        return success_response(None)
    return success_response(UserProfileResponse.model_validate(profile).model_dump())


@router.put("/me", response_model=ApiResponse)
def upsert_my_profile(
    payload: UserProfileUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    profile = UserProfileService(db).upsert(current_user.id, payload)
    return success_response(UserProfileResponse.model_validate(profile).model_dump())
