"""Week 7 API: report endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse, success_response
from app.schemas.report import ReportGenerateRequest, ReportListItem, ReportDetailResponse
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ApiResponse)
def generate_report(
    payload: ReportGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    report = ReportService(db).generate(current_user.id, payload)
    return success_response(ReportDetailResponse.model_validate(report).model_dump())


@router.get("", response_model=ApiResponse)
def list_reports(
    partner_id: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    reports = ReportService(db).list_reports(current_user.id, partner_id)
    items = [ReportListItem.model_validate(r).model_dump() for r in reports]
    return success_response(items)


@router.get("/{report_id}", response_model=ApiResponse)
def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    report = ReportService(db).get_report(current_user.id, report_id)
    return success_response(ReportDetailResponse.model_validate(report).model_dump())
