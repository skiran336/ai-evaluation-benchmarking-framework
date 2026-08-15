# AI Evaluation & Benchmarking Framework

A small, engineering-focused framework for running repeatable AI response evaluations, storing experiment results, and reviewing quality regressions. The project is intentionally built as an **in-progress evaluation platform** rather than a model-training demo.

## Why I built it

AI features need more than a few manual prompts before release. They need repeatable test suites, consistent scoring, failure analysis, and a way to compare experiments over time. This repository explores those building blocks with a simple architecture that can grow from deterministic checks into model-based judging and human review.

## Current capabilities

- JSON-based evaluation test suites
- reusable deterministic scorers:
  - normalized exact match
  - token-level F1
  - required-term coverage
- per-case pass/fail and failure reasons
- experiment metadata including model name and latency
- FastAPI endpoints for suites and evaluation runs
- MongoDB persistence for run history
- React dashboard for run summaries and case-level review
- optional HTTP model-judge adapter with provider-specific integration isolated from the core evaluator
- backend unit tests and GitHub Actions CI

> **Status:** active development. Deterministic evaluation, run storage, the React review UI, and an optional HTTP model-judge adapter are implemented. Direct model-execution adapters and richer run-to-run regression analysis are the next milestones.

## Architecture

```text
JSON Test Suites
      |
      v
   FastAPI
      |
      +---- Deterministic Scorers
      |       exact match / token F1 / required terms
      |
      +---- Model Judge Interface
      |       provider adapter in progress
      |
      v
   MongoDB  <------ React Evaluation Dashboard
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for design notes and the roadmap.

## Repository structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/            # REST endpoints
│   │   ├── core/           # application configuration
│   │   ├── models/         # request/result schemas
│   │   ├── repositories/   # MongoDB run repository
│   │   ├── scorers/        # deterministic + model-judge interfaces
│   │   └── services/       # suite loading and evaluation orchestration
│   └── tests/
├── frontend/               # React/Vite review dashboard
├── test_suites/            # configurable benchmark cases
├── docs/                   # architecture and roadmap
└── docker-compose.yml      # local MongoDB
```

## Quick start

### 1. Start MongoDB

```bash
docker compose up -d
```

### 2. Run the API

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API docs: `http://localhost:8000/docs`

### 3. Create a sample evaluation run

From the repository root:

```bash
curl -X POST http://localhost:8000/api/runs \
  -H 'Content-Type: application/json' \
  --data @examples_run.json
```

Then inspect recent runs:

```bash
curl http://localhost:8000/api/runs
```

### 4. Run the React dashboard

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## API surface

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API and MongoDB health |
| GET | `/api/suites` | List available test suites |
| POST | `/api/runs` | Evaluate supplied model responses and persist a run |
| GET | `/api/runs` | List recent evaluation runs |
| GET | `/api/runs/{id}` | Inspect one run |

## Scoring approach

The first iteration intentionally keeps scoring explainable:

- **Exact match** catches closed-form answers where wording should be stable.
- **Token F1** measures reference overlap without requiring exact phrasing.
- **Required-term coverage** verifies important concepts are present.
- The weighted deterministic score is used for the current pass threshold.

The model-based judge is separated behind an interface so it can be layered on top for open-ended reasoning tasks without coupling evaluation logic to one provider.

## Example benchmark case

```json
{
  "id": "api-idempotency",
  "category": "software_engineering",
  "prompt": "Why is idempotency important for a payment API?",
  "reference_answer": "Idempotency prevents the same payment request from creating duplicate transactions when clients retry after timeouts or network failures.",
  "required_terms": ["duplicate", "retry"]
}
```

## Roadmap

- [x] Configurable JSON test suites
- [x] Deterministic scorer components
- [x] FastAPI evaluation API
- [x] MongoDB run persistence
- [x] React run-review UI
- [x] CI and unit tests
- [x] Optional HTTP model-based judge adapter
- [ ] Direct model execution adapters
- [ ] Side-by-side experiment/regression comparison
- [ ] Human reviewer annotations
- [ ] Benchmark/version metadata and evaluation reports

## Notes on scope

This repository is a portfolio project and uses synthetic benchmark cases. It is not presented as a production-scale evaluation system. The goal is to demonstrate the engineering patterns behind evaluation infrastructure: reusable test suites, scorer isolation, experiment metadata, persistence, failure analysis, and a review workflow.

## Optional model-based judging

The repository includes an optional HTTP model-judge adapter. Set these values in `backend/.env` to enable it:

```text
JUDGE_ENABLED=true
JUDGE_API_URL=http://localhost:9000/judge
JUDGE_API_KEY=
```

The judge service should accept prompt/reference/candidate text and return:

```json
{"score": 0.84, "rationale": "The response covers the key concept but misses one failure mode."}
```

When enabled, the framework stores the judge score/rationale and combines it with the deterministic score for the final case score. Provider-specific authentication or model invocation can be implemented behind this adapter without changing the core evaluation service.
