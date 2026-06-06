"""Evaluation Run Service — workflow-aware regression entrypoint."""
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.repositories.evaluation_repo import EvaluationRepo
from app.models.evaluation_result import EvaluationResult
from app.models.evaluation_run import EvaluationRun
from app.schemas.consultation import ConsultationRequest
from app.schemas.evaluation import EvaluationRunRequest
from app.services.consultation_service import ConsultationService
from app.services.entity_extraction_service import EntityExtractionService
from app.services.intent_router_service import IntentRouterService
from app.services.rule_evaluator_service import RuleEvaluatorService
from app.services.auth_service import AuthService
from app.schemas.auth import UserRegisterRequest
from app.db.repositories.partner_repo import PartnerProfileRepo
from app.utils.ids import generate_uuid


class EvaluationRunService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = EvaluationRepo(db)
        self.intent_router = IntentRouterService()
        self.entity_extractor = EntityExtractionService()
        self.rule_evaluator = RuleEvaluatorService()
        self.consultation_service = ConsultationService(db)
        self.partner_repo = PartnerProfileRepo(db)

    def create_run(self, payload: EvaluationRunRequest) -> EvaluationRun:
        self.repo.seed_default_cases()
        run = EvaluationRun(
            id=generate_uuid(),
            run_name=payload.run_name,
            model_name=payload.model_name,
            prompt_version=payload.prompt_version,
            workflow_version="consultation-v1",
            started_at=datetime.now(timezone.utc),
            status="running",
        )
        return self.repo.create_run(run)

    def execute_run(self, run_id: str) -> EvaluationRun:
        run = self.repo.get_run(run_id)
        if not run:
            raise ValueError("run not found")

        cases = self.repo.load_cases()
        run.total_cases = len(cases)
        passed = 0

        for case in cases:
            result = self._run_single_case(case)
            ev = EvaluationResult(
                id=generate_uuid(),
                run_id=run.id,
                case_id=case.id,
                score_json=result["scores"],
                llm_judge_json=result.get("meta"),
                passed=result["passed"],
            )
            self.repo.save_result(ev)
            if result["passed"]:
                passed += 1

        run.passed_cases = passed
        run.pass_rate = passed / len(cases) if cases else 0
        run.status = "completed"
        run.finished_at = datetime.now(timezone.utc)
        return self.repo.update_run(run)

    def _run_single_case(self, case) -> dict:
        case_type = case.case_type
        if case_type == "workflow":
            return self._run_workflow_case(case)
        return self._run_lightweight_case(case)

    def _run_lightweight_case(self, case) -> dict:
        msg = case.input_payload.get("message", "")
        intent = self.intent_router.detect_intent(msg)
        extraction = self.entity_extractor.extract(msg)
        combined = {
            "intent": intent,
            "entity_name": extraction.get("partner_name"),
            "status": extraction.get("current_status"),
            "goal": extraction.get("current_goal"),
            "answer": "",
        }
        rule_result = self.rule_evaluator.evaluate(
            {"expected_rules": case.expected_rules},
            combined,
        )
        return {
            "scores": rule_result["scores"],
            "passed": rule_result["passed"],
            "meta": {"case_type": case.case_type, "result": combined},
        }

    def _run_workflow_case(self, case) -> dict:
        user_id = self._ensure_eval_user(case.case_name)
        payload = ConsultationRequest(**case.input_payload)
        consultation_result = self.consultation_service.consult(user_id, payload)

        extracted = self.entity_extractor.extract(case.input_payload.get("message", ""))
        combined = {
            "intent": self.intent_router.detect_intent(case.input_payload.get("message", "")),
            "entity_name": extracted.get("partner_name"),
            "status": extracted.get("current_status"),
            "goal": extracted.get("current_goal"),
            "answer": consultation_result.get("answer", ""),
            "auto_created_partner": consultation_result.get("auto_created_partner", False),
            "memory_updated": consultation_result.get("memory_updated", False),
            "structured_result": consultation_result.get("structured_result"),
        }

        rule_result = self.rule_evaluator.evaluate(
            {"expected_rules": case.expected_rules},
            combined,
        )

        return {
            "scores": rule_result["scores"],
            "passed": rule_result["passed"],
            "meta": {
                "case_type": "workflow",
                "consultation_result": consultation_result,
                "partner_count": len(self.partner_repo.list_by_user_id(user_id)),
            },
        }

    def _ensure_eval_user(self, case_name: str) -> str:
        email = f"eval_{case_name}@example.com".lower()
        auth_service = AuthService(self.db)
        try:
            user = auth_service.register(email, "password123")
            return user.id
        except Exception:
            data = auth_service.login(email, "password123")
            return data["user"].id

    def get_run(self, run_id: str) -> EvaluationRun:
        return self.repo.get_run(run_id)

    def list_runs(self) -> list[EvaluationRun]:
        return self.repo.list_runs()
