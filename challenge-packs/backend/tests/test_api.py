import os

from fastapi.testclient import TestClient

from app import create_app


def build_client():
    os.environ["DATA_DIR"] = os.path.join(os.getcwd(), "data", "visible")
    os.environ["BENCHMARK_FIXTURES_FILE"] = os.path.join(
        os.getcwd(), "data", "visible", "benchmarks.json"
    )
    return TestClient(create_app())


def test_health_has_backend_status_fields():
    client = build_client()

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"] == "ok"
    assert payload["benchmark_service"] in {"ok", "fixture"}


def test_campaign_performance_returns_complete_contract():
    client = build_client()

    response = client.get("/campaigns/cmp-001/performance")

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "campaign_id": "cmp-001",
        "campaign_name": "Spring Launch",
        "totals": {
            "total_impressions": 5000,
            "total_clicks": 212,
            "total_conversions": 21,
            "total_spend": 890.0,
            "total_revenue": 3230.0,
            "ctr": 0.0424,
            "cvr": 0.0991,
            "roas": 3.6292,
        },
    }


def test_top_creators_honors_limit_and_order():
    client = build_client()

    response = client.get("/creators/top", params={"campaign_id": "cmp-001", "limit": 2})

    assert response.status_code == 200
    payload = response.json()
    assert payload["campaign_id"] == "cmp-001"
    assert payload["limit"] == 2
    assert [row["creator_id"] for row in payload["creators"]] == ["crt-001", "crt-002"]
    assert payload["creators"][0]["total_conversions"] == 12
    assert payload["creators"][0]["total_clicks"] == 110
    assert payload["creators"][0]["ctr"] == 0.05


def test_anomalies_returns_threshold_violations_with_expected_shape():
    client = build_client()

    response = client.get("/campaigns/cmp-002/anomalies")

    assert response.status_code == 200
    payload = response.json()
    assert payload["campaign_id"] == "cmp-002"
    assert payload["thresholds"] == {"min_ctr": 0.03, "min_roas": 2.5}
    assert payload["alerts"] == [
        {
            "metric_date": "2026-01-03",
            "issues": ["ctr_below_threshold", "roas_below_threshold"],
            "ctr": 0.0263,
            "roas": 2.2059,
        }
    ]


def test_anomalies_returns_empty_alerts_when_no_thresholds_are_violated():
    client = build_client()

    response = client.get("/campaigns/cmp-003/anomalies")

    assert response.status_code == 200
    payload = response.json()
    assert payload["campaign_id"] == "cmp-003"
    assert payload["alerts"] == []
