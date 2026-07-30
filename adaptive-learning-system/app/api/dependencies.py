"""FastAPI dependencies shared by application routers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Annotated, Protocol, TypeVar

from fastapi import Depends, Request
from pydantic import BaseModel

from app.config import Settings
from app.errors import AppError


ModelT = TypeVar("ModelT", bound=BaseModel)


class LLMClient(Protocol):
    """Provider-neutral structured generation used by Phase 2 workflows."""

    def generate_structured(
        self,
        messages: Sequence[Mapping[str, str]],
        response_model: type[ModelT],
        temperature: float | None = None,
    ) -> ModelT:
        """Return provider output validated against ``response_model``."""


def get_app_settings(request: Request) -> Settings:
    """Return the settings instance attached during application creation."""

    settings = getattr(request.app.state, "settings", None)
    if not isinstance(settings, Settings):
        raise RuntimeError("Application settings are not initialized.")
    return settings


def get_llm_client(request: Request) -> LLMClient:
    """Resolve an application-scoped LLM adapter when one has been registered."""

    client = getattr(request.app.state, "llm_client", None)
    if client is None:
        raise AppError(
            code="LLM_UNAVAILABLE",
            message="The language model service is not configured.",
            status_code=503,
        )
    return client


SettingsDependency = Annotated[Settings, Depends(get_app_settings)]
LLMDependency = Annotated[LLMClient, Depends(get_llm_client)]
