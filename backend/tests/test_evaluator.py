import json
from pathlib import Path
from app.models.schemas import RunRequest
from app.services.evaluator import EvaluationService
from app.services.suites import SuiteService


def test_evaluation_run(tmp_path: Path):
    suite = {
        "name": "tiny",
        "description": "tiny suite",
        "cases": [
            {
                "id": "c1",
                "category": "knowledge",
                "prompt": "What is Kafka?",
                "reference_answer": "Kafka is a distributed event streaming platform.",
                "required_terms": ["event", "streaming"],
            }
        ],
    }
    (tmp_path / "tiny.json").write_text(json.dumps(suite), encoding="utf-8")
    service = EvaluationService(SuiteService(str(tmp_path)))
    request = RunRequest.model_validate(
        {
            "suite_name": "tiny",
            "model_name": "demo-model",
            "responses": [
                {
                    "case_id": "c1",
                    "response": "Kafka is an event streaming platform.",
                    "latency_ms": 120,
                }
            ],
        }
    )
    result = service.evaluate(request)
    assert result.suite_name == "tiny"
    assert result.average_score > 0
    assert result.average_latency_ms == 120
