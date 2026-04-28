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

Expected response contract:

- `GET /health` should return at least:
  - `status`: `"ok"` when all dependencies are reachable, otherwise `"degraded"`
  - `database`: `"ok"` or `"error"`
  - `benchmark_service`: `"ok"`, `"fixture"`, or `"error"`
  - `dataset`: the active dataset name if one is configured
- `GET /campaigns/{campaign_id}/performance` should return:
  - top-level `campaign_id` and `campaign_name`
  - `totals.total_impressions`
  - `totals.total_clicks`
  - `totals.total_conversions`
  - `totals.total_spend`
  - `totals.total_revenue`
  - `totals.ctr`
  - `totals.cvr`
  - `totals.roas`
- `GET /creators/top` should return top-level `campaign_id`, `limit`, and a `creators` array.
- `GET /campaigns/{campaign_id}/anomalies` should return top-level `campaign_id`, `thresholds`, and an `alerts` array. Each alert should include `metric_date`, `issues`, `ctr`, and `roas`.

Metric rules:

- `ctr` is `total_clicks / total_impressions`.
- `cvr` is `total_conversions / total_clicks`.
- `roas` is `total_revenue / total_spend`.
- Round derived rates to 4 decimal places and money totals to 2 decimal places.
- Treat null revenue as `0` for aggregate totals and ROAS.
- Use safe division for zero denominators. Do not crash or fabricate infinite values.
- A missing campaign should return a clear `404`.

Creator ranking rules:

- Rank creators by total conversions descending.
- Break ties by total clicks descending.
- Break remaining ties by `creator_id` ascending for deterministic output.
- Honor `limit`, including values other than the visible sample default.

Anomaly rules:

- Roll up metrics by day before comparing to thresholds.
- A single day may have multiple issues.
- Include `ctr_below_threshold` when daily CTR is below `min_ctr`.
- Include `roas_below_threshold` when daily ROAS is below `min_roas`.
- Include `spend_without_conversions` when daily spend is positive and daily conversions are zero.
- Campaigns with no threshold violations should return an empty `alerts` array.

### 2. SQL Analytics

**Files:** `sql/campaign_performance.sql`, `sql/top_creators.sql`, `sql/daily_anomalies.sql`

These queries are intentionally wrong.

Your fixes should be robust to:

- hidden datasets with ties
- rows with zero impressions or zero spend
- null revenue values
- campaigns that should return no anomalies
- campaigns that should produce multiple anomaly reasons on the same day

Do not hardcode results from the visible sample data. The grader runs your SQL against additional hidden datasets with the same contract but different values and edge cases.

### 3. Tests

**File:** `tests/test_api.py`

The provided tests are incomplete. You should make them pass and improve the suite so it exercises meaningful backend behavior.

At minimum, your final tests should cover:

- one complete campaign performance response, including all totals and derived rates
- one ranking/limit case that proves deterministic creator ordering
- at least one anomaly case with threshold violations
- at least one non-happy-path behavior such as missing campaigns, downstream failure handling, zero-denominator data, or a campaign with no anomalies

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
