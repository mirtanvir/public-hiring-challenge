import json
import os
from pathlib import Path

import duckdb
import httpx
from fastapi import FastAPI, HTTPException, Query


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"
VISIBLE_DATA_DIR = PROJECT_ROOT / "data" / "visible"


def _load_connection():
    conn = duckdb.connect(":memory:")
    conn.execute(
        "CREATE OR REPLACE VIEW campaigns AS "
        f"SELECT * FROM read_csv_auto('{VISIBLE_DATA_DIR / 'campaigns.csv'}', header=true)"
    )
    conn.execute(
        "CREATE OR REPLACE VIEW creators AS "
        f"SELECT * FROM read_csv_auto('{VISIBLE_DATA_DIR / 'creators.csv'}', header=true)"
    )
    conn.execute(
        "CREATE OR REPLACE VIEW campaign_daily_metrics AS "
        f"SELECT * FROM read_csv_auto('{VISIBLE_DATA_DIR / 'campaign_daily_metrics.csv'}', header=true)"
    )
    return conn


def _read_sql(name: str) -> str:
    return (SQL_DIR / name).read_text()


def _load_benchmark_thresholds(campaign_id: str) -> dict:
    fixture_file = os.getenv("BENCHMARK_FIXTURES_FILE")
    if fixture_file:
      data = json.loads(Path(fixture_file).read_text())
      if campaign_id in data:
          return data[campaign_id]

    base_url = os.getenv("BENCHMARK_API_BASE", "http://127.0.0.1:8091")
    try:
        response = httpx.get(f"{base_url}/benchmarks/{campaign_id}", timeout=2.0)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {"min_ctr": 0.05, "min_roas": 3.0}


def _row_to_dict(columns, row):
    data = {}
    for column, value in zip(columns, row):
        if isinstance(value, float):
            data[column] = round(value, 4)
        else:
            data[column] = value
    return data


def create_app() -> FastAPI:
    app = FastAPI(title="Campaign Analytics Service")
    conn = _load_connection()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/campaigns/{campaign_id}/performance")
    def campaign_performance(campaign_id: str):
        query = _read_sql("campaign_performance.sql")
        result = conn.execute(query, [campaign_id]).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="campaign not found")
        columns = [description[0] for description in conn.description]
        return {"campaign_id": campaign_id, "metrics": _row_to_dict(columns, result)}

    @app.get("/creators/top")
    def top_creators(campaign_id: str = Query(...), limit: int = Query(3, ge=1, le=10)):
        query = _read_sql("top_creators.sql")
        rows = conn.execute(query, [campaign_id, limit]).fetchall()
        columns = [description[0] for description in conn.description]
        return {
            "campaign_id": campaign_id,
            "limit": limit,
            "items": [_row_to_dict(columns, row) for row in rows],
        }

    @app.get("/campaigns/{campaign_id}/anomalies")
    def anomalies(campaign_id: str):
        thresholds = _load_benchmark_thresholds(campaign_id)
        query = _read_sql("daily_anomalies.sql")
        rows = conn.execute(query, [campaign_id]).fetchall()
        columns = [description[0] for description in conn.description]

        alerts = []
        for row in rows:
            payload = _row_to_dict(columns, row)
            issues = []
            ctr = payload.get("ctr") or 0
            roas = payload.get("roas") or 0
            if ctr < thresholds["min_ctr"]:
                issues.append("ctr_below_threshold")
            if roas < thresholds["min_roas"]:
                issues.append("roas_below_threshold")
            if issues:
                payload["issues"] = issues
                alerts.append(payload)

        return {"campaign_id": campaign_id, "alerts": alerts}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
