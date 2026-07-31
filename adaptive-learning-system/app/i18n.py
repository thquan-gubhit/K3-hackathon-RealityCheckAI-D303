"""Internationalization context for the backend."""

import contextvars

# Stores the requested language code for the current request (e.g. "vi", "en")
request_language: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_language", default="en"
)
