"""Week 5 API: relationship-memory endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse, success_response
from app.schemas.relationship_memory import RelationshipProfileSnapshot, MemorySummaryData
from app.schemas.relationship_memory_expanded import (
    RelationshipMemoryResponse,
    RelationshipProfilePatchRequest,
)
from app.services.relationship_memory_service import RelationshipMemoryService

router = APIRouter(prefix="/relationship-memory", tags=["relationship-memory"])


@router.get("/{partner_id}", response_model=ApiResponse)
def get_relationship_memory(
    partner_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    data = RelationshipMemoryService(db).get_memory(current_user.id, partner_id)
    return success_response(data)


@router.patch("/{partner_id}/profile", response_model=ApiResponse)
def patch_relationship_profile(
    partner_id: str,
    payload: RelationshipProfilePatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    profile = RelationshipMemoryService(db).patch_profile(
        current_user.id, partner_id, payload.model_dump(exclude_unset=True)
    )
    return success_response(RelationshipProfileSnapshot.model_validate(profile).model_dump())
