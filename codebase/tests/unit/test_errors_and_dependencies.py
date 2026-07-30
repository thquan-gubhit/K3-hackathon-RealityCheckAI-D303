"""Tests for stable application errors and request-scoped dependencies."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.api.dependencies import get_app_settings, get_llm_client
from app.config import Settings
from app.errors import AppError


def test_app_error_exposes_stable_envelope() -> None:
    error = AppError(
        "DOCUMENT_NOT_FOUND",
        "The requested document does not exist.",
        status_code=404,
        details={"document_id": "DOC_001"},
    )

    assert error.status == 404
    assert error.status_code == 404
    assert str(error) == "The requested document does not exist."
    assert error.to_dict(request_id="request-1") == {
        "error": {
            "code": "DOCUMENT_NOT_FOUND",
            "message": "The requested document does not exist.",
            "details": {"document_id": "DOC_001"},
            "request_id": "request-1",
        }
    }


def test_app_error_accepts_status_alias() -> None:
    error = AppError("MAP_NOT_READY", "Map is not ready.", status=409)

    assert error.status == 409
    assert error.status_code == 409


def test_app_settings_dependency_reads_application_state() -> None:
    settings = Settings(
        _env_file=None,
        database_url="sqlite:///:memory:",
        upload_dir="./data/uploads",
    )
    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(settings=settings))
    )

    assert get_app_settings(request) is settings


def test_llm_dependency_fails_with_stable_unavailable_error() -> None:
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace()))

    with pytest.raises(AppError) as captured:
        get_llm_client(request)

    assert captured.value.code == "LLM_UNAVAILABLE"
    assert captured.value.status_code == 503
