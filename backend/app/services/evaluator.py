from statistics import mean
from uuid import uuid4
from app.models.schemas import CaseScore, EvaluationRun, RunRequest
from app.scorers.deterministic import combined_score
from app.scorers.model_judge import ModelJudge
from app.services.suites import SuiteService


PASS_THRESHOLD = 0.62


class EvaluationService:
    def __init__(self, suite_service: SuiteService, judge: ModelJudge | None = None):
        self.suite_service = suite_service
        self.judge = judge

    def evaluate(self, request: RunRequest) -> EvaluationRun:
        suite = self.suite_service.load(request.suite_name)
        response_map = {response.case_id: response for response in request.responses}
        scores: list[CaseScore] = []

        for case in suite.cases:
            response = response_map.get(case.id)
            if response is None:
                scores.append(
                    CaseScore(
                        case_id=case.id,
                        category=case.category,
                        exact_match=0,
                        token_f1=0,
                        required_terms_score=0,
                        deterministic_score=0,
                        judge_score=None,
                        judge_rationale=None,
                        final_score=0,
                        latency_ms=None,
                        passed=False,
                        failure_reasons=["missing_response"],
                    )
                )
                continue

            metrics = combined_score(response.response, case.reference_answer, case.required_terms)
            judge_score = None
            judge_rationale = None
            if self.judge is not None:
                result = self.judge.score(
                    prompt=case.prompt,
                    reference=case.reference_answer,
                    candidate=response.response,
                )
                judge_score = round(result.score, 4)
                judge_rationale = result.rationale

            final_score = metrics["deterministic_score"]
            if judge_score is not None:
                final_score = round((0.6 * final_score) + (0.4 * judge_score), 4)

            failure_reasons: list[str] = []
            if metrics["required_terms_score"] < 1:
                failure_reasons.append("missing_required_terms")
            if metrics["token_f1"] < 0.35:
                failure_reasons.append("low_reference_overlap")

            scores.append(
                CaseScore(
                    case_id=case.id,
                    category=case.category,
                    latency_ms=response.latency_ms,
                    judge_score=judge_score,
                    judge_rationale=judge_rationale,
                    final_score=final_score,
                    passed=final_score >= PASS_THRESHOLD,
                    failure_reasons=failure_reasons,
                    **metrics,
                )
            )

        average_score = mean(score.final_score for score in scores) if scores else 0
        pass_rate = mean(1.0 if score.passed else 0.0 for score in scores) if scores else 0
        latencies = [score.latency_ms for score in scores if score.latency_ms is not None]

        return EvaluationRun(
            id=str(uuid4()),
            suite_name=suite.name,
            model_name=request.model_name,
            average_score=round(average_score, 4),
            pass_rate=round(pass_rate, 4),
            average_latency_ms=round(mean(latencies), 2) if latencies else None,
            scores=scores,
        )
