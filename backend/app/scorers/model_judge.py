from dataclasses import dataclass
from typing import Protocol
import httpx


@dataclass
class JudgeResult:
    score: float
    rationale: str


class ModelJudge(Protocol):
    def score(self, *, prompt: str, reference: str, candidate: str) -> JudgeResult:
        ...


class HttpModelJudge:
    """Optional adapter for a model-judge service.

    The configured endpoint receives prompt/reference/candidate text and must
    return JSON shaped like: {"score": 0.0-1.0, "rationale": "..."}.
    Keeping this contract small isolates provider-specific code from the core
    evaluation pipeline.
    """

    def __init__(self, api_url: str, api_key: str | None = None, timeout_seconds: float = 20.0):
        self.api_url = api_url
        self.api_key = api_key
        self.timeout_seconds = timeout_seconds

    def score(self, *, prompt: str, reference: str, candidate: str) -> JudgeResult:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = httpx.post(
            self.api_url,
            headers=headers,
            json={
                "task": "Score the candidate response against the prompt and reference answer from 0 to 1.",
                "prompt": prompt,
                "reference": reference,
                "candidate": candidate,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        raw_score = float(payload["score"])
        return JudgeResult(
            score=max(0.0, min(1.0, raw_score)),
            rationale=str(payload.get("rationale", "")),
        )
