"""Evaluation schemas — Week 8."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class EvaluationRunRequest(BaseModel):
    run_name: str = Field(default="regression-run")
    model_name: str = Field(default="deepseek-chat")
    prompt_version: str = Field(default="v1")

class EvaluationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str; run_name: str; model_name: str; status: str
    total_cases: int; passed_cases: int; pass_rate: float | None
    started_at: datetime; finished_at: datetime | None

class EvaluationCaseItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str; case_name: str; case_type: str

class EvaluationResultItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str; case_id: str; passed: bool
    score_json: dict; llm_judge_json: dict | None
    created_at: datetime
