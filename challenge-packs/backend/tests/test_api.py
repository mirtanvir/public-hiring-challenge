import os

from fastapi.testclient import TestClient

from app import create_app


def build_client():
    os.environ["DATA_DIR"] = os.path.join(os.getcwd(), "data", "visible")
    os.environ["BENCHMARK_FIXTURES_FILE"] = os.path.join(
        os.getcwd(), "data", "visible", "benchmarks.json"
    )
    os.environ.pop("BENCHMARK_API_BASE", None)
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
    assert payload == {
        "campaign_id": "cmp-001",
        "limit": 2,
        "creators": [
            {
                "campaign_id": "cmp-001",
                "creator_id": "crt-001",
                "creator_name": "Avery",
                "total_impressions": 2200,
                "total_clicks": 110,
                "total_conversions": 12,
                "total_spend": 420.0,
                "ctr": 0.05,
            },
            {
                "campaign_id": "cmp-001",
                "creator_id": "crt-002",
                "creator_name": "Blake",
                "total_impressions": 2000,
                "total_clicks": 70,
                "total_conversions": 6,
                "total_spend": 350.0,
                "ctr": 0.035,
            },
        ],
    }


def test_top_creators_breaks_ties_by_creator_id_after_conversions_and_clicks():
    client = build_client()

    response = client.get("/creators/top", params={"campaign_id": "cmp-004", "limit": 2})

    assert response.status_code == 200
    payload = response.json()
    assert [row["creator_id"] for row in payload["creators"]] == ["crt-003", "crt-004"]
    assert [row["total_conversions"] for row in payload["creators"]] == [3, 3]
    assert [row["total_clicks"] for row in payload["creators"]] == [30, 30]


def test_anomalies_returns_threshold_violations_with_expected_shape():
    client = build_client()

    response = client.get("/campaigns/cmp-002/anomalies")

    assert response.status_code == 200
    payload = response.json()
    assert payload == {
        "campaign_id": "cmp-002",
        "thresholds": {"min_ctr": 0.03, "min_roas": 2.5},
        "alerts": [
            {
                "metric_date": "2026-01-03",
                "issues": ["ctr_below_threshold", "roas_below_threshold"],
                "ctr": 0.0263,
                "roas": 2.2059,
            }
        ],
    }


def test_anomalies_supports_spend_without_conversions():
    client = build_client()

    response = client.get("/campaigns/cmp-005/anomalies")

    assert response.status_code == 200
    payload = response.json()
    assert payload["thresholds"] == {"min_ctr": 0.03, "min_roas": 1.0}
    assert payload["alerts"] == [
        {
            "metric_date": "2026-01-06",
            "issues": ["roas_below_threshold", "spend_without_conversions"],
            "ctr": 0.05,
            "roas": 0.0,
        }
    ]


def test_anomalies_returns_empty_alerts_when_no_thresholds_are_violated():
    client = build_client()

    response = client.get("/campaigns/cmp-003/anomalies")

    assert response.status_code == 200
    payload = response.json()
    assert payload["campaign_id"] == "cmp-003"
    assert payload["alerts"] == []


def test_anomalies_benchmark_service_unreachable():
    os.environ["DATA_DIR"] = os.path.join(os.getcwd(), "data", "visible")
    os.environ.pop("BENCHMARK_FIXTURES_FILE", None)
    os.environ["BENCHMARK_API_BASE"] = "http://localhost:19999"
    client = TestClient(create_app())

    response = client.get("/campaigns/cmp-001/anomalies")

    assert response.status_code == 502
