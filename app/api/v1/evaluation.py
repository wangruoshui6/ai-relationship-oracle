"""Week 8 API: evaluation endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.common import ApiResponse, success_response
from app.schemas.evaluation import EvaluationRunRequest, EvaluationRunResponse, EvaluationResultItem
from app.services.evaluation_run_service import EvaluationRunService
from app.db.repositories.evaluation_repo import EvaluationRepo

router = APIRouter(prefix="/evaluation", tags=["evaluation"])

@router.post("/runs", response_model=ApiResponse)
def create_evaluation_run(payload: EvaluationRunRequest, db: Session = Depends(get_db)) -> dict:
    svc = EvaluationRunService(db)
    run = svc.create_run(payload)
    run = svc.execute_run(run.id)
    return success_response(EvaluationRunResponse.model_validate(run).model_dump())

@router.get("/runs", response_model=ApiResponse)
def list_evaluation_runs(db: Session = Depends(get_db)) -> dict:
    runs = EvaluationRunService(db).list_runs()
    return success_response([EvaluationRunResponse.model_validate(r).model_dump() for r in runs])

@router.get("/runs/{run_id}", response_model=ApiResponse)
def get_evaluation_run(run_id: str, db: Session = Depends(get_db)) -> dict:
    repo = EvaluationRepo(db)
    run = repo.get_run(run_id)
    results = repo.list_results(run_id)
    return success_response({
        "run": EvaluationRunResponse.model_validate(run).model_dump(),
        "results": [EvaluationResultItem.model_validate(r).model_dump() for r in results]
    })
