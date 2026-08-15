import re
from collections import Counter


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def exact_match(candidate: str, reference: str) -> float:
    normalize = lambda value: " ".join(_tokens(value))
    return 1.0 if normalize(candidate) == normalize(reference) else 0.0


def token_f1(candidate: str, reference: str) -> float:
    candidate_tokens = _tokens(candidate)
    reference_tokens = _tokens(reference)
    if not candidate_tokens or not reference_tokens:
        return 0.0

    common = Counter(candidate_tokens) & Counter(reference_tokens)
    overlap = sum(common.values())
    if overlap == 0:
        return 0.0

    precision = overlap / len(candidate_tokens)
    recall = overlap / len(reference_tokens)
    return 2 * precision * recall / (precision + recall)


def required_terms_score(candidate: str, required_terms: list[str]) -> float:
    if not required_terms:
        return 1.0
    normalized = candidate.lower()
    matched = sum(1 for term in required_terms if term.lower() in normalized)
    return matched / len(required_terms)


def combined_score(candidate: str, reference: str, required_terms: list[str]) -> dict[str, float]:
    exact = exact_match(candidate, reference)
    f1 = token_f1(candidate, reference)
    terms = required_terms_score(candidate, required_terms)
    # Exact match is useful but intentionally low-weight for open-ended answers.
    score = (0.15 * exact) + (0.55 * f1) + (0.30 * terms)
    return {
        "exact_match": round(exact, 4),
        "token_f1": round(f1, 4),
        "required_terms_score": round(terms, 4),
        "deterministic_score": round(score, 4),
    }
