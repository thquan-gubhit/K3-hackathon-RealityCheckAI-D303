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
