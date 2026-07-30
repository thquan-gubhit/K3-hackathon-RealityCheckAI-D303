"""Health endpoint integration tests."""

from __future__ import annotations


def test_health_endpoint_reports_ready(api_client) -> None:
    """The app starts without a real LLM and exposes its health contract."""

    response = api_client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["app_name"] == "Adaptive Learning System Test"
    assert payload["environment"] == "test"
    assert payload["database"] == "configured"
