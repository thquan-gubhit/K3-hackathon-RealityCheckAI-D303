"""Phase 6 request correlation and stable error-envelope tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def _app(tmp_path):
    settings = Settings(
        _env_file=None,
        app_env="test",
        debug=False,
        database_url=f"sqlite:///{(tmp_path / 'errors.db').as_posix()}",
        upload_dir=tmp_path / "uploads",
        llm_api_key="fake-key",
        llm_base_url="https://llm.invalid/v1",
        llm_model="fake-model",
    )
    return create_app(settings, llm_client=object())


def test_request_id_is_generated_and_safe_caller_id_is_preserved(
    tmp_path,
) -> None:
    application = _app(tmp_path)
    with TestClient(application) as client:
        generated = client.get("/health")
        supplied = client.get(
            "/health",
            headers={"X-Request-ID": "demo-request:42"},
        )
        rejected = client.get(
            "/health",
            headers={"X-Request-ID": "unsafe request"},
        )

    assert generated.headers["X-Request-ID"]
    assert supplied.headers["X-Request-ID"] == "demo-request:42"
    assert rejected.headers["X-Request-ID"] != "unsafe request"


def test_validation_and_route_errors_use_stable_envelopes(tmp_path) -> None:
    application = _app(tmp_path)
    with TestClient(application) as client:
        validation = client.get("/documents?limit=0")
        missing_route = client.get("/route-that-does-not-exist")

    assert validation.status_code == 422
    assert validation.json()["error"]["code"] == "VALIDATION_ERROR"
    assert validation.json()["error"]["request_id"]
    assert validation.json()["error"]["details"]["fields"] == [
        {"location": "query.limit", "type": "greater_than_equal"}
    ]
    assert missing_route.status_code == 404
    assert missing_route.json()["error"]["code"] == "ROUTE_NOT_FOUND"
    assert missing_route.json()["error"]["request_id"]


def test_unexpected_error_does_not_expose_exception_message(tmp_path) -> None:
    application = _app(tmp_path)
    secret = "sk-must-never-be-returned-123456"

    @application.get("/test-only-unexpected")
    def unexpected() -> None:
        raise RuntimeError(f"provider failed with {secret}")

    with TestClient(
        application,
        raise_server_exceptions=False,
    ) as client:
        response = client.get("/test-only-unexpected")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert response.json()["error"]["request_id"]
    assert secret not in response.text
