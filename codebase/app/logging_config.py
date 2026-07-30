"""Structured logging utilities shared by application entry points."""

from __future__ import annotations

from datetime import UTC, datetime
import json
import logging


class JsonLogFormatter(logging.Formatter):
    """Render standard logging records as valid one-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, str] = {
            "time": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)
