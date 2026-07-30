"""Shared mapping from bounded LLM/domain failures to stable API errors."""

from __future__ import annotations

from app.errors import AppError
from app.llm import (
    InvalidLLMOutputError,
    LLMProviderError,
    LLMTimeoutError,
)
from app.services.question_service import AssessmentServiceError


def assessment_app_error(exc: Exception) -> AppError:
    """Return a transport-safe error without provider payloads or source text."""

    if isinstance(exc, LLMTimeoutError):
        return AppError(
            "LLM_TIMEOUT",
            "The language model timed out. Please retry.",
            status_code=504,
        )
    if isinstance(exc, InvalidLLMOutputError):
        return AppError(
            "LLM_INVALID_OUTPUT",
            "The language model returned invalid structured output.",
            status_code=502,
        )
    if isinstance(exc, LLMProviderError):
        return AppError(
            "LLM_PROVIDER_ERROR",
            "The language model provider request failed.",
            status_code=502,
        )
    if isinstance(exc, AssessmentServiceError):
        status = 404 if exc.code.endswith("_NOT_FOUND") else 422
        return AppError(exc.code, str(exc), status_code=status)
    return AppError(
        "ASSESSMENT_FAILED",
        "The assessment operation failed.",
        status_code=500,
    )


__all__ = ["assessment_app_error"]
