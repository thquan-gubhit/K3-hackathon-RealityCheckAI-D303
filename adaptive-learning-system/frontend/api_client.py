"""Small HTTP helpers used by the Streamlit user interface.

The frontend intentionally treats the backend as the source of all business
logic.  This module only handles transport concerns and turns connection
failures into messages that the UI can present safely.
"""

from __future__ import annotations

import json
import os
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import requests
from dotenv import dotenv_values


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Retain only the frontend value instead of importing LLM secrets into this process.
_DOTENV_BACKEND_API_URL = dotenv_values(PROJECT_ROOT / ".env").get(
    "BACKEND_API_URL"
)


@dataclass(frozen=True)
class HealthCheckResult:
    """Result of attempting to contact the backend health endpoint."""

    available: bool
    message: str
    payload: dict[str, Any] | None = None


class BackendApiError(Exception):
    """A safe, display-ready failure returned by the backend client."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "BACKEND_REQUEST_FAILED",
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


def get_backend_api_url() -> str:
    """Return the configured backend base URL without a trailing slash."""

    configured_url = (
        os.getenv("BACKEND_API_URL")
        or _DOTENV_BACKEND_API_URL
        or ""
    ).strip()
    return configured_url.rstrip("/")


def check_backend_health(
    backend_api_url: str | None = None,
    *,
    timeout_seconds: float = 3.0,
) -> HealthCheckResult:
    """Check backend availability without leaking transport errors to the UI."""

    base_url = (backend_api_url or get_backend_api_url()).rstrip("/")
    if not base_url:
        return HealthCheckResult(
            available=False,
            message="BACKEND_API_URL is not configured.",
        )

    try:
        request = Request(
            f"{base_url}/health",
            headers={"Accept": "application/json"},
            method="GET",
        )
        with urlopen(request, timeout=timeout_seconds) as response:
            status_code = response.getcode()
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return HealthCheckResult(
            available=False,
            message=f"Backend responded with HTTP {exc.code}.",
        )
    except (TimeoutError, socket.timeout):
        return HealthCheckResult(
            available=False,
            message="Backend health check timed out.",
        )
    except URLError:
        return HealthCheckResult(
            available=False,
            message="Could not connect to the backend.",
        )
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HealthCheckResult(
            available=False,
            message="Backend returned an invalid health response.",
        )
    except (OSError, ValueError):
        return HealthCheckResult(
            available=False,
            message="The backend URL or response is invalid.",
        )

    if status_code != 200:
        return HealthCheckResult(
            available=False,
            message=f"Backend responded with HTTP {status_code}.",
        )
    required_text_fields = ("app_name", "environment", "database")
    if (
        not isinstance(payload, dict)
        or payload.get("status") != "ok"
        or any(
            not isinstance(payload.get(field), str) or not payload[field]
            for field in required_text_fields
        )
    ):
        return HealthCheckResult(
            available=False,
            message="Backend returned an invalid health response.",
        )

    return HealthCheckResult(
        available=True,
        message="Backend is online.",
        payload=payload,
    )


def _require_backend_api_url(backend_api_url: str | None = None) -> str:
    """Return a configured backend URL or raise a display-safe error."""

    base_url = (backend_api_url or get_backend_api_url()).rstrip("/")
    if not base_url:
        raise BackendApiError(
            "BACKEND_API_URL is not configured.",
            code="BACKEND_NOT_CONFIGURED",
        )
    return base_url


def _request_json(
    method: str,
    path: str,
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 30.0,
    files: dict[str, tuple[str, bytes, str]] | None = None,
    json_body: dict[str, Any] | None = None,
) -> Any:
    """Send one backend request and decode its JSON response."""

    base_url = _require_backend_api_url(backend_api_url)
    headers = {"Accept": "application/json"}
    
    try:
        import streamlit as st
        lang = st.session_state.get("ui_language", "vi")
        if lang == "English":
            lang = "en"
        elif lang == "Tiếng Việt":
            lang = "vi"
        headers["Accept-Language"] = lang
    except Exception:
        pass

    try:
        response = requests.request(
            method,
            f"{base_url}{path}",
            headers=headers,
            files=files,
            json=json_body,
            timeout=timeout_seconds,
        )
    except requests.Timeout as exc:
        raise BackendApiError(
            "The backend request timed out. Please try again.",
            code="BACKEND_TIMEOUT",
        ) from exc
    except requests.RequestException as exc:
        raise BackendApiError(
            "Could not connect to the backend.",
            code="BACKEND_UNAVAILABLE",
        ) from exc

    try:
        payload = response.json()
    except (ValueError, json.JSONDecodeError) as exc:
        if 200 <= response.status_code < 300:
            raise BackendApiError(
                "Backend returned an invalid response.",
                code="INVALID_BACKEND_RESPONSE",
                status_code=response.status_code,
            ) from exc
        raise BackendApiError(
            f"Backend responded with HTTP {response.status_code}.",
            code="BACKEND_REQUEST_FAILED",
            status_code=response.status_code,
        ) from exc

    if not 200 <= response.status_code < 300:
        error = payload.get("error") if isinstance(payload, dict) else None
        if isinstance(error, dict):
            code = error.get("code")
            message = error.get("message")
            details = error.get("details")
        else:
            code = None
            message = payload.get("detail") if isinstance(payload, dict) else None
            details = None
        raise BackendApiError(
            message
            if isinstance(message, str) and message
            else f"Backend responded with HTTP {response.status_code}.",
            code=code if isinstance(code, str) and code else "BACKEND_REQUEST_FAILED",
            status_code=response.status_code,
            details=details if isinstance(details, dict) else None,
        )

    return payload


def _expect_object(payload: Any, *, operation: str) -> dict[str, Any]:
    """Require one JSON object from a successful backend response."""

    if not isinstance(payload, dict):
        raise BackendApiError(
            f"Backend returned an invalid {operation} response.",
            code="INVALID_BACKEND_RESPONSE",
        )
    return payload


def _expect_object_list(payload: Any, *, operation: str) -> list[dict[str, Any]]:
    """Require a JSON list containing objects only."""

    if not isinstance(payload, list) or any(
        not isinstance(item, dict) for item in payload
    ):
        raise BackendApiError(
            f"Backend returned an invalid {operation} response.",
            code="INVALID_BACKEND_RESPONSE",
        )
    return payload


def upload_document(
    filename: str,
    content: bytes,
    *,
    content_type: str = "application/pdf",
    backend_api_url: str | None = None,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    """Upload one PDF and return the backend's direct Document object."""

    payload = _request_json(
        "POST",
        "/documents/upload",
        backend_api_url=backend_api_url,
        timeout_seconds=timeout_seconds,
        files={"file": (filename, content, content_type)},
    )
    return _expect_object(payload, operation="document upload")


def process_document(
    document_id: str,
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 120.0,
) -> dict[str, Any]:
    """Start synchronous Phase 2 processing and validate its result envelope."""

    safe_id = quote(document_id, safe="")
    payload = _expect_object(
        _request_json(
            "POST",
            f"/documents/{safe_id}/process",
            backend_api_url=backend_api_url,
            timeout_seconds=timeout_seconds,
        ),
        operation="document processing",
    )
    if (
        not isinstance(payload.get("document"), dict)
        or not isinstance(payload.get("knowledge_units"), list)
        or any(
            not isinstance(unit, dict)
            for unit in payload.get("knowledge_units", [])
        )
        or not isinstance(payload.get("coverage"), dict)
    ):
        raise BackendApiError(
            "Backend returned an invalid document processing response.",
            code="INVALID_BACKEND_RESPONSE",
        )
    return payload


def list_documents(
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 10.0,
) -> list[dict[str, Any]]:
    """Return the direct Document list from the backend."""

    payload = _request_json(
        "GET",
        "/documents",
        backend_api_url=backend_api_url,
        timeout_seconds=timeout_seconds,
    )
    # Direct lists are the Phase 2 contract.  The wrappers keep the UI tolerant
    # of pagination being introduced later without spreading transport details.
    if isinstance(payload, dict):
        payload = payload.get("documents", payload.get("items"))
    return _expect_object_list(payload, operation="document list")


def get_document(
    document_id: str,
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 10.0,
) -> dict[str, Any]:
    """Fetch one direct Document object."""

    safe_id = quote(document_id, safe="")
    payload = _request_json(
        "GET",
        f"/documents/{safe_id}",
        backend_api_url=backend_api_url,
        timeout_seconds=timeout_seconds,
    )
    return _expect_object(payload, operation="document detail")


def get_knowledge_map(
    document_id: str,
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    """Fetch and normalize the Knowledge Map response for one document."""

    safe_id = quote(document_id, safe="")
    raw_payload = _request_json(
        "GET",
        f"/documents/{safe_id}/knowledge-map",
        backend_api_url=backend_api_url,
        timeout_seconds=timeout_seconds,
    )
    if isinstance(raw_payload, list):
        payload: dict[str, Any] = {
            "document_id": document_id,
            "status": "ready",
            "knowledge_units": raw_payload,
        }
    else:
        payload = _expect_object(raw_payload, operation="knowledge map")
        if "knowledge_units" not in payload and isinstance(payload.get("items"), list):
            payload = {**payload, "knowledge_units": payload["items"]}

    units = payload.get("knowledge_units")
    if not isinstance(units, list) or any(
        not isinstance(unit, dict) for unit in units
    ):
        raise BackendApiError(
            "Backend returned an invalid knowledge map response.",
            code="INVALID_BACKEND_RESPONSE",
        )
    return payload


def get_knowledge_unit(
    unit_id: str,
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 10.0,
) -> dict[str, Any]:
    """Fetch one direct Knowledge Unit object."""

    safe_id = quote(unit_id, safe="")
    payload = _request_json(
        "GET",
        f"/knowledge-units/{safe_id}",
        backend_api_url=backend_api_url,
        timeout_seconds=timeout_seconds,
    )
    return _expect_object(payload, operation="knowledge unit detail")


def list_knowledge_unit_questions(
    unit_id: str,
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 10.0,
) -> list[dict[str, Any]]:
    """Return learner-safe accepted questions for one Knowledge Unit."""

    safe_id = quote(unit_id, safe="")
    payload = _request_json(
        "GET",
        f"/knowledge-units/{safe_id}/questions",
        backend_api_url=backend_api_url,
        timeout_seconds=timeout_seconds,
    )
    return _expect_object_list(payload, operation="question list")


def generate_questions(
    unit_id: str,
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 120.0,
) -> dict[str, Any]:
    """Generate the mandatory learner-safe question set."""

    safe_id = quote(unit_id, safe="")
    return _expect_object(
        _request_json(
            "POST",
            f"/knowledge-units/{safe_id}/generate-questions",
            backend_api_url=backend_api_url,
            timeout_seconds=timeout_seconds,
        ),
        operation="question generation",
    )


def create_learning_session(
    document_id: str,
    knowledge_unit_id: str,
    *,
    user_id: str = "local-user",
    backend_api_url: str | None = None,
    timeout_seconds: float = 120.0,
) -> dict[str, Any]:
    """Create a session and ensure its mandatory questions exist."""

    return _expect_object(
        _request_json(
            "POST",
            "/learning-sessions",
            backend_api_url=backend_api_url,
            timeout_seconds=timeout_seconds,
            json_body={
                "user_id": user_id,
                "document_id": document_id,
                "knowledge_unit_id": knowledge_unit_id,
            },
        ),
        operation="learning session creation",
    )


def get_learning_session(
    session_id: str,
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 10.0,
) -> dict[str, Any]:
    safe_id = quote(session_id, safe="")
    return _expect_object(
        _request_json(
            "GET",
            f"/learning-sessions/{safe_id}",
            backend_api_url=backend_api_url,
            timeout_seconds=timeout_seconds,
        ),
        operation="learning session",
    )


def get_next_question(
    session_id: str,
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    """Return the next rule-selected activity."""

    safe_id = quote(session_id, safe="")
    return _expect_object(
        _request_json(
            "GET",
            f"/learning-sessions/{safe_id}/next-question",
            backend_api_url=backend_api_url,
            timeout_seconds=timeout_seconds,
        ),
        operation="next question",
    )


def submit_answer(
    session_id: str,
    question_id: str,
    user_answer: str,
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 120.0,
) -> dict[str, Any]:
    """Submit free text for rubric-based evaluation and mastery update."""

    safe_id = quote(session_id, safe="")
    return _expect_object(
        _request_json(
            "POST",
            f"/learning-sessions/{safe_id}/answers",
            backend_api_url=backend_api_url,
            timeout_seconds=timeout_seconds,
            json_body={
                "question_id": question_id,
                "user_answer": user_answer,
            },
        ),
        operation="answer evaluation",
    )


def finish_unit(
    session_id: str,
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    safe_id = quote(session_id, safe="")
    return _expect_object(
        _request_json(
            "POST",
            f"/learning-sessions/{safe_id}/finish-unit",
            backend_api_url=backend_api_url,
            timeout_seconds=timeout_seconds,
        ),
        operation="unit completion",
    )


def get_progress(
    user_id: str = "local-user",
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    safe_id = quote(user_id, safe="")
    return _expect_object(
        _request_json(
            "GET",
            f"/progress/{safe_id}",
            backend_api_url=backend_api_url,
            timeout_seconds=timeout_seconds,
        ),
        operation="progress",
    )


def get_unit_progress(
    user_id: str,
    unit_id: str,
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    safe_user = quote(user_id, safe="")
    safe_unit = quote(unit_id, safe="")
    return _expect_object(
        _request_json(
            "GET",
            f"/progress/{safe_user}/knowledge-units/{safe_unit}",
            backend_api_url=backend_api_url,
            timeout_seconds=timeout_seconds,
        ),
        operation="unit progress",
    )


def run_tutor_agent(
    session_id: str,
    *,
    reason: str = "EXPLICIT_DIFFERENT_EXPLANATION",
    backend_api_url: str | None = None,
    timeout_seconds: float = 120.0,
) -> dict[str, Any]:
    safe_id = quote(session_id, safe="")
    return _expect_object(
        _request_json(
            "POST",
            f"/learning-sessions/{safe_id}/agent/run",
            backend_api_url=backend_api_url,
            timeout_seconds=timeout_seconds,
            json_body={"reason": reason},
        ),
        operation="Tutor Agent run",
    )


def get_agent_traces(
    session_id: str,
    *,
    backend_api_url: str | None = None,
    timeout_seconds: float = 30.0,
) -> list[dict[str, Any]]:
    safe_id = quote(session_id, safe="")
    payload = _request_json(
        "GET",
        f"/learning-sessions/{safe_id}/agent/traces",
        backend_api_url=backend_api_url,
        timeout_seconds=timeout_seconds,
    )
    return _expect_object_list(payload, operation="Tutor Agent traces")
