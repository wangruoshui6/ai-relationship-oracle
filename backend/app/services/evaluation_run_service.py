"""Evaluation Run Service — Week 8."""
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.repositories.evaluation_repo import EvaluationRepo
from app.models.evaluation_run import EvaluationRun
from app.schemas.evaluation import EvaluationRunRequest
from app.services.intent_router_service import IntentRouterService
from app.services.entity_extraction_service import EntityExtractionService
from app.services.rule_evaluator_service import RuleEvaluatorService
from app.models.evaluation_result import EvaluationResult
from app.utils.ids import generate_uuid

class EvaluationRunService:
    def __init__(self, db: Session) -> None:
        self.db = db; self.repo = EvaluationRepo(db)
        self.intent_router = IntentRouterService()
        self.entity_extractor = EntityExtractionService()
        self.rule_evaluator = RuleEvaluatorService()

    def create_run(self, payload: EvaluationRunRequest) -> EvaluationRun:
        self.repo.seed_default_cases()
        run = EvaluationRun(
            id=generate_uuid(), run_name=payload.run_name,
            model_name=payload.model_name, prompt_version=payload.prompt_version,
            started_at=datetime.now(timezone.utc), status="running"
        )
        return self.repo.create_run(run)

    def execute_run(self, run_id: str) -> EvaluationRun:
        run = self.repo.get_run(run_id)
        if not run: raise ValueError("run not found")
        cases = self.repo.load_cases()
        run.total_cases = len(cases)
        passed = 0

        for case in cases:
            result = self._run_single_case(case)
            ev = EvaluationResult(
                id=generate_uuid(), run_id=run.id, case_id=case.id,
                score_json=result["scores"], llm_judge_json=result.get("llm_judge"),
                passed=result["passed"]
            )
            self.repo.save_result(ev)
            if result["passed"]: passed += 1

        run.passed_cases = passed
        run.pass_rate = passed / len(cases) if cases else 0
        run.status = "completed"
        run.finished_at = datetime.now(timezone.utc)
        return self.repo.update_run(run)

    def _run_single_case(self, case) -> dict:
        msg = case.input_payload.get("message", "")
        intent = self.intent_router.detect_intent(msg)
        extraction = self.entity_extractor.extract(msg)
        combined = {"intent": intent, "entity_name": extraction.get("partner_name"),
                     "status": extraction.get("current_status"), "goal": extraction.get("current_goal"),
                     "answer": ""}
        rule_result = self.rule_evaluator.evaluate(
            {"expected_rules": case.expected_rules}, combined
        )
        return {"scores": rule_result["scores"], "passed": rule_result["passed"]}

    def get_run(self, run_id: str) -> EvaluationRun:
        return self.repo.get_run(run_id)

    def list_runs(self) -> list[EvaluationRun]:
        return self.repo.list_runs()
