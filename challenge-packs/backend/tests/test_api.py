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


def test_campaign_performance_returns_expected_totals():
    client = build_client()

    response = client.get("/campaigns/cmp-001/performance")

    assert response.status_code == 200
    payload = response.json()
    assert payload["campaign_id"] == "cmp-001"
    assert payload["campaign_name"] == "Spring Launch"
    assert payload["totals"]["total_impressions"] == 5000
    assert payload["totals"]["total_conversions"] == 21
    assert payload["totals"]["ctr"] == 0.0424


def test_top_creators_honors_limit_and_order():
    client = build_client()

    response = client.get("/creators/top", params={"campaign_id": "cmp-001", "limit": 2})

    assert response.status_code == 200
    payload = response.json()
    assert payload["campaign_id"] == "cmp-001"
    assert payload["limit"] == 2
    assert [row["creator_id"] for row in payload["creators"]] == ["crt-001", "crt-002"]
