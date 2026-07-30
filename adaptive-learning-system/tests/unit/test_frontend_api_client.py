"""Tests for the frontend's transport-only backend client."""

from __future__ import annotations

from urllib.error import URLError

import pytest

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


class FakeJsonResponse:
    """Small requests-compatible response used by transport tests."""

    def __init__(self, status_code: int, payload: object) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> object:
        return self._payload


def test_upload_document_sends_pdf_as_multipart(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_request(method, url, **kwargs):
        captured.update(method=method, url=url, **kwargs)
        return FakeJsonResponse(
            201,
            {
                "id": "DOC_001",
                "original_filename": "lesson.pdf",
                "status": "uploaded",
            },
        )

    monkeypatch.setattr(api_client.requests, "request", fake_request)

    result = api_client.upload_document(
        "lesson.pdf",
        b"%PDF-test",
        backend_api_url="http://backend.invalid/",
    )

    assert result["id"] == "DOC_001"
    assert captured["method"] == "POST"
    assert captured["url"] == "http://backend.invalid/documents/upload"
    assert captured["files"] == {
        "file": ("lesson.pdf", b"%PDF-test", "application/pdf")
    }


def test_list_documents_accepts_direct_list_contract(monkeypatch) -> None:
    monkeypatch.setattr(
        api_client.requests,
        "request",
        lambda *args, **kwargs: FakeJsonResponse(
            200,
            [{"id": "DOC_001"}, {"id": "DOC_002"}],
        ),
    )

    documents = api_client.list_documents(
        backend_api_url="http://backend.invalid"
    )

    assert [document["id"] for document in documents] == [
        "DOC_001",
        "DOC_002",
    ]


def test_process_document_validates_phase_two_envelope(monkeypatch) -> None:
    monkeypatch.setattr(
        api_client.requests,
        "request",
        lambda *args, **kwargs: FakeJsonResponse(
            200,
            {
                "document": {"id": "DOC_001", "status": "processed"},
                "knowledge_units": [{"id": "KU_001"}],
                "coverage": {
                    "readable_pages": 3,
                    "covered_pages": 3,
                    "coverage_ratio": 1.0,
                },
            },
        ),
    )

    result = api_client.process_document(
        "DOC_001",
        backend_api_url="http://backend.invalid",
    )

    assert result["knowledge_units"][0]["id"] == "KU_001"
    assert result["coverage"]["coverage_ratio"] == 1.0


def test_knowledge_map_accepts_exact_response_shape(monkeypatch) -> None:
    monkeypatch.setattr(
        api_client.requests,
        "request",
        lambda *args, **kwargs: FakeJsonResponse(
            200,
            {
                "document_id": "DOC_001",
                "status": "ready",
                "knowledge_units": [{"id": "KU_001"}],
            },
        ),
    )

    result = api_client.get_knowledge_map(
        "DOC_001",
        backend_api_url="http://backend.invalid",
    )

    assert result == {
        "document_id": "DOC_001",
        "status": "ready",
        "knowledge_units": [{"id": "KU_001"}],
    }


def test_backend_error_envelope_becomes_display_safe_exception(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        api_client.requests,
        "request",
        lambda *args, **kwargs: FakeJsonResponse(
            404,
            {
                "error": {
                    "code": "DOCUMENT_NOT_FOUND",
                    "message": "The requested document does not exist.",
                    "details": {"document_id": "DOC_missing"},
                }
            },
        ),
    )

    with pytest.raises(api_client.BackendApiError) as captured:
        api_client.get_document(
            "DOC_missing",
            backend_api_url="http://backend.invalid",
        )

    assert captured.value.code == "DOCUMENT_NOT_FOUND"
    assert captured.value.status_code == 404
    assert captured.value.details == {"document_id": "DOC_missing"}
    assert str(captured.value) == "The requested document does not exist."


def test_document_ids_are_url_encoded(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_request(method, url, **kwargs):
        captured["url"] = url
        return FakeJsonResponse(200, {"id": "DOC/unsafe"})

    monkeypatch.setattr(api_client.requests, "request", fake_request)

    api_client.get_document(
        "DOC/unsafe",
        backend_api_url="http://backend.invalid",
    )

    assert captured["url"] == "http://backend.invalid/documents/DOC%2Funsafe"


def test_submit_answer_sends_json_body_and_encoded_session_id(
    monkeypatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_request(method, url, **kwargs):
        captured.update(
            {
                "method": method,
                "url": url,
                "json": kwargs.get("json"),
            }
        )
        return FakeJsonResponse(200, {"attempt": {}, "evaluation": {}})

    monkeypatch.setattr(api_client.requests, "request", fake_request)

    api_client.submit_answer(
        "SESSION/unsafe",
        "Q_001",
        "My answer",
        backend_api_url="http://backend.invalid",
    )

    assert captured == {
        "method": "POST",
        "url": (
            "http://backend.invalid/learning-sessions/"
            "SESSION%2Funsafe/answers"
        ),
        "json": {
            "question_id": "Q_001",
            "user_answer": "My answer",
        },
    }
