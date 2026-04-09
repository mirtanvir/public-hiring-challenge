# Backend Engineer (Python + SQL) Take-Home Challenge

This repository contains an intentionally flawed backend analytics service. The exercise is designed for a backend engineer with at least 3 years of experience. Your goal is to turn this into a production-usable service, not just make the happy path work on the visible sample data.

## How to Submit

1. Clone this repository locally.
2. Fix the service, SQL, tests, and packaging issues described below.
3. Push your changes and open a pull request against `main`.

> **Important:** Opening a pull request is your final submission. Once you create a PR, grading begins immediately and the repository will be locked to read-only on your final attempt.

Your 24-hour timer started automatically when you provisioned this repo through the challenge portal. Grading results will be posted directly to your PR.

## What You Need to Fix

### 1. Backend API

**Primary file:** `python/app.py`

The service should run on FastAPI and expose these endpoints:

- `GET /health`
- `GET /campaigns/{campaign_id}/performance`
- `GET /creators/top?campaign_id=...&limit=...`
- `GET /campaigns/{campaign_id}/anomalies`

Behavior contract:

- The service must load analytics data from the directory configured by `DATA_DIR`, not from a hardcoded visible sample path.
- `GET /health` should report whether the database is reachable and whether the benchmark service is reachable.
- `GET /campaigns/{campaign_id}/performance` should return one aggregated campaign record with stable numeric fields.
- `GET /creators/top` should honor the `limit` parameter and return creators in the expected ranking order.
- `GET /campaigns/{campaign_id}/anomalies` should call the benchmark service, compare daily rollups against benchmark thresholds, and return meaningful alerts.
- Downstream benchmark failures should be surfaced as a backend error response, not silently ignored.

### 2. SQL Analytics

**Files:** `sql/campaign_performance.sql`, `sql/top_creators.sql`, `sql/daily_anomalies.sql`

These queries are intentionally wrong.

Your fixes should be robust to:

- hidden datasets with ties
- rows with zero impressions or zero spend
- null revenue values
- campaigns that should return no anomalies
- campaigns that should produce multiple anomaly reasons on the same day

Do not hardcode results from the visible sample data. The grader runs your SQL against additional hidden datasets.

### 3. Tests

**File:** `tests/test_api.py`

The provided tests are incomplete. You should make them pass and improve the suite so it exercises meaningful backend behavior.

At minimum, your final tests should cover:

- one happy-path analytics response
- one ranking/limit case
- at least one non-happy-path behavior such as downstream failure handling or an edge-case dataset condition

### 4. Packaging

**File:** `python/Dockerfile`

The Dockerfile should build and run the service cleanly on port `8080`.

You do not need cloud credentials or external infrastructure to complete this exercise.

### 5. Engineering Notes

**File:** `DECISIONS.md`

Fill in the template with a short explanation of:

- how you approached the SQL fixes
- which edge cases you handled
- what tests you added or improved
- any tradeoffs you made

## Local Development

The visible sample data lives in `data/visible/`.

Typical local commands:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r python/requirements.txt
export DATA_DIR="$(pwd)/data/visible"
export BENCHMARK_FIXTURES_FILE="$(pwd)/data/visible/benchmarks.json"
PYTHONPATH=python uvicorn app:app --host 127.0.0.1 --port 8080
```

Run tests:

```bash
export DATA_DIR="$(pwd)/data/visible"
export BENCHMARK_FIXTURES_FILE="$(pwd)/data/visible/benchmarks.json"
PYTHONPATH=python pytest tests/test_api.py -q
```

## Scoring

Your submission is scored on a weighted rubric across:

- SQL correctness and hidden-data robustness
- Python/API behavior
- test quality
- engineering notes
- Docker build/run

The grader uses hidden scenarios in addition to the visible sample, so aim for correctness and robustness rather than sample-specific fixes.
