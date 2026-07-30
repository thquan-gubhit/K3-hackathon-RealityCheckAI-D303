"""Tests for the frontend's transport-only backend client."""

from __future__ import annotations

from urllib.error import URLError

from frontend import api_client


def test_backend_url_comes_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("BACKEND_API_URL", "http://backend.example:9000/")

    assert api_client.get_backend_api_url() == "http://backend.example:9000"


def test_health_check_requires_configured_backend_url(monkeypatch) -> None:
    monkeypatch.delenv("BACKEND_API_URL", raising=False)
    monkeypatch.setattr(api_client, "_DOTENV_BACKEND_API_URL", None)

    result = api_client.check_backend_health()

    assert result.available is False
    assert result.message == "BACKEND_API_URL is not configured."


def test_health_check_handles_connection_failure(monkeypatch) -> None:
    def raise_connection_error(*args, **kwargs):
        raise URLError("offline")

    monkeypatch.setattr(api_client, "urlopen", raise_connection_error)

    result = api_client.check_backend_health("http://backend.invalid")

    assert result.available is False
    assert result.payload is None
    assert result.message == "Could not connect to the backend."


def test_health_check_rejects_non_ok_payload(monkeypatch) -> None:
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def getcode(self):
            return 200

        def read(self):
            return b'{"status":"down"}'

    monkeypatch.setattr(api_client, "urlopen", lambda *args, **kwargs: FakeResponse())

    result = api_client.check_backend_health("http://backend.invalid")

    assert result.available is False
    assert result.message == "Backend returned an invalid health response."


def test_health_check_handles_malformed_url() -> None:
    result = api_client.check_backend_health("not a valid URL")

    assert result.available is False
    assert result.message == "The backend URL or response is invalid."
