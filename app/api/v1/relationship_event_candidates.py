"""Week 5 API: relationship-event-candidates endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.repositories.relationship_event_repo import RelationshipEventRepo
from app.models.user import User
from app.schemas.common import ApiResponse, success_response
from app.schemas.relationship_memory_expanded import EventCandidateItem, RelationshipEventItem
from app.services.memory_update_service import MemoryUpdateService

router = APIRouter(prefix="/relationship-event-candidates", tags=["relationship-event-candidates"])


@router.get("", response_model=ApiResponse)
def list_candidates(
    partner_id: str = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    repo = RelationshipEventRepo(db)
    candidates = repo.list_pending_candidates(current_user.id, partner_id)
    items = [EventCandidateItem.model_validate(c).model_dump() for c in candidates]
    return success_response(items)


@router.post("/{candidate_id}/confirm", response_model=ApiResponse)
def confirm_candidate(
    candidate_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    event = MemoryUpdateService(db).confirm_candidate(candidate_id, current_user.id)
    return success_response(RelationshipEventItem.model_validate(event).model_dump())


@router.post("/{candidate_id}/reject", response_model=ApiResponse)
def reject_candidate(
    candidate_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    candidate = MemoryUpdateService(db).reject_candidate(candidate_id, current_user.id)
    return success_response({"id": candidate.id, "status": candidate.candidate_status})
