"""Shared pytest fixtures.

Tests use a temporary SQLite database and inert LLM credentials so the suite
never touches local application data or a real model provider.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def stable_debug_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Neutralize unrelated host-level DEBUG values during every test."""

    monkeypatch.setenv("DEBUG", "false")


@pytest.fixture
def isolated_app_environment(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> dict[str, str]:
    """Configure isolated dependencies before importing the FastAPI app."""

    database_path = tmp_path / "test.db"
    values = {
        "APP_NAME": "Adaptive Learning System Test",
        "APP_ENV": "test",
        "DEBUG": "false",
        "DATABASE_URL": f"sqlite:///{database_path.as_posix()}",
        "UPLOAD_DIR": str(tmp_path / "uploads"),
        "LLM_API_KEY": "test-key-not-real",
        "LLM_BASE_URL": "https://llm.invalid/v1",
        "LLM_MODEL": "test-model-not-real",
        "AGENT_ENABLED": "false",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)
    return values


@pytest.fixture
def api_client(
    isolated_app_environment: dict[str, str],
) -> Iterator["TestClient"]:
    """Yield a FastAPI client configured with temporary local dependencies."""

    from fastapi.testclient import TestClient

    from app.config import get_settings

    if hasattr(get_settings, "cache_clear"):
        get_settings.cache_clear()

    from app.main import app

    with TestClient(app) as client:
        yield client

    if hasattr(get_settings, "cache_clear"):
        get_settings.cache_clear()
