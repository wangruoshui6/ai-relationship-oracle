from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.consultations import router as consultations_router
from app.api.v1.conversations import router as conversations_router
from app.api.v1.evaluation import router as evaluation_router
from app.api.v1.partners import router as partners_router
from app.api.v1.profiles import router as profiles_router
from app.api.v1.relationship_event_candidates import router as event_candidates_router
from app.api.v1.relationship_memory import router as relationship_memory_router
from app.api.v1.reports import router as reports_router
from app.api.v1.structured_consultations import router as structured_consultations_router
from app.schemas.common import success_response

api_router = APIRouter(prefix="/api/v1")
@api_router.get("/health")
def health_check() -> dict:
    return success_response({"status": "ok"})

api_router.include_router(auth_router)
api_router.include_router(profiles_router)
api_router.include_router(partners_router)
api_router.include_router(consultations_router)
api_router.include_router(conversations_router)
api_router.include_router(relationship_memory_router)
api_router.include_router(event_candidates_router)
api_router.include_router(reports_router)
api_router.include_router(evaluation_router)
api_router.include_router(structured_consultations_router)
