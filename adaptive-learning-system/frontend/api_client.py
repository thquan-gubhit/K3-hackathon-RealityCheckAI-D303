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
from urllib.request import Request, urlopen

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
