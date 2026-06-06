"""Evaluation Repository — Week 8."""
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.evaluation_case import EvaluationCase
from app.models.evaluation_result import EvaluationResult
from app.models.evaluation_run import EvaluationRun

class EvaluationRepo:
    def __init__(self, db: Session) -> None:
        self.db = db

    def load_cases(self) -> list[EvaluationCase]:
        return list(self.db.scalars(select(EvaluationCase)).all())

    def create_run(self, run: EvaluationRun) -> EvaluationRun:
        self.db.add(run); self.db.commit(); self.db.refresh(run); return run

    def save_result(self, result: EvaluationResult) -> EvaluationResult:
        self.db.add(result); self.db.commit(); self.db.refresh(result); return result

    def get_run(self, run_id: str) -> EvaluationRun | None:
        return self.db.scalar(select(EvaluationRun).where(EvaluationRun.id == run_id))

    def update_run(self, run: EvaluationRun) -> EvaluationRun:
        self.db.add(run); self.db.commit(); self.db.refresh(run); return run

    def list_runs(self) -> list[EvaluationRun]:
        return list(self.db.scalars(select(EvaluationRun).order_by(EvaluationRun.started_at.desc())).all())

    def list_results(self, run_id: str) -> list[EvaluationResult]:
        return list(self.db.scalars(
            select(EvaluationResult).where(EvaluationResult.run_id == run_id)
        ).all())

    def seed_default_cases(self) -> None:
        existing = self.db.scalar(select(func.count()).select_from(EvaluationCase))
        if existing and existing > 0:
            return
        cases = [
            EvaluationCase(case_name="breakup_detection", case_type="intent_router",
                input_payload={"message": "I broke up with Sarah 3 months ago"},
                expected_rules={"intent": "relationship_analysis", "entity_name": "Sarah", "status": "breakup"}),
            EvaluationCase(case_name="greeting_classification", case_type="intent_router",
                input_payload={"message": "Hello, how are you?"},
                expected_rules={"intent": "greeting"}),
            EvaluationCase(case_name="entity_not_found", case_type="entity_extraction",
                input_payload={"message": "The weather is nice today"},
                expected_rules={"entity_name": None, "status": None, "goal": None}),
            EvaluationCase(case_name="chinese_breakup", case_type="entity_extraction",
                input_payload={"message": "我和李静分手了"},
                expected_rules={"entity_name": "李静", "status": "breakup"}),
            EvaluationCase(case_name="neutral_entity_check", case_type="entity_extraction",
                input_payload={"message": "I feel sad about my breakup"},
                expected_rules={"entity_name": None, "status": None}),
            EvaluationCase(case_name="workflow_auto_partner_bootstrap", case_type="workflow",
                input_payload={
                    "message": "I broke up with Sarah three months ago, will she come back?",
                    "analysis_methods": ["bazi", "psychology"]
                },
                expected_rules={
                    "intent": "relationship_analysis",
                    "entity_name": "Sarah",
                    "status": "breakup",
                    "expects_partner_created": True,
                    "expects_memory_updated": True,
                    "requires_answer": True,
                    "no_absolute_prediction": True,
                }),
        ]
        for c in cases:
            self.db.add(c)
        self.db.commit()
