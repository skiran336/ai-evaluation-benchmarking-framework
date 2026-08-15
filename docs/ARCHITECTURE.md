# Architecture

## Current MVP

```text
Evaluation test suites (JSON)
            |
            v
      FastAPI service
            |
            +--> deterministic scorers
            |      - normalized exact match
            |      - token F1
            |      - required-term coverage
            |
            +--> optional HTTP model-judge adapter
            |
            v
         MongoDB
            |
            v
       React dashboard
```

## Why this structure

- **Test suites are data, not code.** New benchmarks can be added without changing evaluator logic.
- **Scorers are reusable components.** The service can combine deterministic checks with a model-based judge.
- **Runs are persisted.** Storing per-case scores, latency, failure reasons, suite, and model metadata enables comparison and regression analysis.
- **UI is review-oriented.** The first interface focuses on run summaries and failed cases rather than model chat functionality.

## Next implementation milestones

1. Add direct model response-generation adapters so a run can execute against configured models.
2. Add run-to-run regression comparison by case and category.
3. Add human reviewer annotations and agreement tracking.
4. Add benchmark versioning and richer quality metrics.
