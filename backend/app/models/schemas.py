from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field


class EvaluationCase(BaseModel):
    id: str
    category: str
    prompt: str
    reference_answer: str
    required_terms: list[str] = Field(default_factory=list)


class EvaluationSuite(BaseModel):
    name: str
    description: str
    cases: list[EvaluationCase]


class CandidateResponse(BaseModel):
    case_id: str
    response: str
    latency_ms: float | None = Field(default=None, ge=0)


class RunRequest(BaseModel):
    suite_name: str
    model_name: str
    responses: list[CandidateResponse]


class CaseScore(BaseModel):
    case_id: str
    category: str
    exact_match: float
    token_f1: float
    required_terms_score: float
    deterministic_score: float
    judge_score: float | None = None
    judge_rationale: str | None = None
    final_score: float
    latency_ms: float | None = None
    passed: bool
    failure_reasons: list[str] = Field(default_factory=list)


class EvaluationRun(BaseModel):
    id: str
    suite_name: str
    model_name: str
    status: Literal["completed", "failed"] = "completed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    average_score: float
    pass_rate: float
    average_latency_ms: float | None = None
    scores: list[CaseScore]
