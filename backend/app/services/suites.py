import json
from pathlib import Path
from app.models.schemas import EvaluationSuite


class SuiteService:
    def __init__(self, suites_dir: str):
        path = Path(suites_dir)
        if not path.is_absolute():
            path = (Path(__file__).resolve().parents[3] / path).resolve()
        self.suites_dir = path

    def list_suites(self) -> list[str]:
        if not self.suites_dir.exists():
            return []
        return sorted(file.stem for file in self.suites_dir.glob("*.json"))

    def load(self, name: str) -> EvaluationSuite:
        file_path = self.suites_dir / f"{name}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Unknown suite: {name}")
        with file_path.open("r", encoding="utf-8") as handle:
            return EvaluationSuite.model_validate(json.load(handle))
