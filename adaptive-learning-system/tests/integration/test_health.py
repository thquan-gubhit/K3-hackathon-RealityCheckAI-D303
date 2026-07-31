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


def test_local_prototype_origin_can_call_backend(api_client) -> None:
    """The VLearn prototype may call the API without a wildcard CORS policy."""

    response = api_client.options(
        "/health",
        headers={
            "Origin": "http://127.0.0.1:8899",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"]
        == "http://127.0.0.1:8899"
    )


def test_backend_serves_integrated_vlearn_ui(api_client) -> None:
    response = api_client.get("/vlearn/")
    script = api_client.get("/vlearn/backend-integration.js")
    stylesheet = api_client.get("/vlearn/backend-integration.css")

    assert response.status_code == 200
    assert "VLearn · Nói Lại Đi" in response.text
    assert "backend-integration.js" in response.text
    assert script.status_code == 200
    assert '"/documents/upload"' in script.text
    assert '"/learning-sessions"' in script.text
    assert stylesheet.status_code == 200
    assert ".live-ku" in stylesheet.text
