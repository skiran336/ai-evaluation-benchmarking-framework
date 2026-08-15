from fastapi import APIRouter, HTTPException
from app.core.config import get_settings
from app.models.schemas import EvaluationRun, RunRequest
from app.repositories.runs import RunRepository
from app.scorers.model_judge import HttpModelJudge
from app.services.evaluator import EvaluationService
from app.services.suites import SuiteService

router = APIRouter()
settings = get_settings()
suite_service = SuiteService(settings.suites_dir)
judge = None
if settings.judge_enabled and settings.judge_api_url:
    judge = HttpModelJudge(settings.judge_api_url, settings.judge_api_key or None)
evaluation_service = EvaluationService(suite_service, judge=judge)
repository = RunRepository(settings.mongodb_uri, settings.mongodb_db)


@router.get("/health")
def health() -> dict[str, str]:
    try:
        repository.ping()
        database = "connected"
    except Exception:
        database = "unavailable"
    return {
        "status": "ok",
        "mongodb": database,
        "model_judge": "enabled" if judge is not None else "disabled",
    }


@router.get("/suites")
def list_suites() -> dict[str, list[str]]:
    return {"suites": suite_service.list_suites()}


@router.post("/runs", response_model=EvaluationRun)
def create_run(request: RunRequest) -> EvaluationRun:
    try:
        run = evaluation_service.evaluate(request)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Evaluation failed: {exc}") from exc

    document = run.model_dump(mode="json")
    try:
        repository.insert(document)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"MongoDB unavailable: {exc}") from exc
    return run


@router.get("/runs")
def list_runs(limit: int = 20) -> list[dict]:
    try:
        return repository.list_recent(min(max(limit, 1), 100))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"MongoDB unavailable: {exc}") from exc


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict:
    try:
        run = repository.get(run_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"MongoDB unavailable: {exc}") from exc
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
