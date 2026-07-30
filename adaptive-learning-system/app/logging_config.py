"""Structured logging utilities shared by application entry points."""

from __future__ import annotations

from datetime import UTC, datetime
import json
import logging
import re


_BEARER_PATTERN = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{8,}")
_AUTHORIZATION_PATTERN = re.compile(
    r"(?i)\bauthorization(\s*[:=]\s*)(?:bearer\s+)?[^\s,;]+"
)
_PROVIDER_KEY_PATTERN = re.compile(r"\bsk-[A-Za-z0-9_-]{8,}")
_SECRET_ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|authorization|password|access[_-]?token)"
    r"(\s*[:=]\s*)(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)"
)
_MAX_LOG_VALUE_LENGTH = 4_000


def redact_log_value(value: object) -> str:
    """Remove credential-shaped data and bound one serialized log field."""

    text = str(value)
    text = _AUTHORIZATION_PATTERN.sub(
        lambda match: f"authorization{match.group(1)}[REDACTED]",
        text,
    )
    text = _SECRET_ASSIGNMENT_PATTERN.sub(
        lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]",
        text,
    )
    text = _BEARER_PATTERN.sub("Bearer [REDACTED]", text)
    text = _PROVIDER_KEY_PATTERN.sub("[REDACTED]", text)
    if len(text) > _MAX_LOG_VALUE_LENGTH:
        text = text[:_MAX_LOG_VALUE_LENGTH] + "…[TRUNCATED]"
    return text


class JsonLogFormatter(logging.Formatter):
    """Render standard logging records as valid one-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, str] = {
            "time": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": redact_log_value(record.getMessage()),
        }
        if record.exc_info:
            payload["exception"] = redact_log_value(
                self.formatException(record.exc_info)
            )
        return json.dumps(payload, ensure_ascii=False)


__all__ = ["JsonLogFormatter", "redact_log_value"]
