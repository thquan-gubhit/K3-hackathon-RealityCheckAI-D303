"""Tests for structured application logging."""

from __future__ import annotations

import json
import logging

from app.logging_config import JsonLogFormatter


def test_json_log_formatter_escapes_message_content() -> None:
    """Quotes and newlines remain valid JSON rather than breaking log records."""

    record = logging.LogRecord(
        name="adaptive-learning.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=12,
        msg='quoted "value"\nand next line',
        args=(),
        exc_info=None,
    )

    payload = json.loads(JsonLogFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "adaptive-learning.test"
    assert payload["message"] == 'quoted "value"\nand next line'


def test_json_log_formatter_redacts_credentials_and_bounds_content() -> None:
    secret = "sk-example-secret-value-123456"
    record = logging.LogRecord(
        name="adaptive-learning.security",
        level=logging.ERROR,
        pathname=__file__,
        lineno=30,
        msg=(
            f"authorization=Bearer abcdefghijklmnop api_key={secret} "
            f"password=hunter2 {'source text ' * 500}"
        ),
        args=(),
        exc_info=None,
    )

    payload = json.loads(JsonLogFormatter().format(record))

    assert secret not in payload["message"]
    assert "abcdefghijklmnop" not in payload["message"]
    assert "hunter2" not in payload["message"]
    assert payload["message"].count("[REDACTED]") == 3
    assert payload["message"].endswith("…[TRUNCATED]")
