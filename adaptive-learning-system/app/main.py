"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from typing import AsyncIterator

from fastapi import FastAPI, Request
from pydantic import BaseModel

from app.config import ConfigurationError, Settings, get_settings
from app.logging_config import JsonLogFormatter


logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Stable response contract for local readiness checks."""

    status: str
    app_name: str
    environment: str
    database: str


def _configure_logging(settings: Settings) -> None:
    """Configure valid JSON application logs once."""

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))

    for handler in root_logger.handlers:
        if getattr(handler, "_adaptive_learning_json", False):
            handler.setLevel(getattr(logging, settings.log_level))
            return

    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, settings.log_level))
    handler.setFormatter(JsonLogFormatter())
    handler._adaptive_learning_json = True  # type: ignore[attr-defined]
    root_logger.addHandler(handler)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Validate runtime configuration before accepting traffic."""

    settings: Settings = application.state.settings
    _configure_logging(settings)
    try:
        settings.validate_runtime_requirements()
    except ConfigurationError as exc:
        logger.error("startup_configuration_error: %s", exc)
        raise

    application.state.settings = settings
    application.title = settings.app_name
    logger.info(
        "application_started app=%s environment=%s",
        settings.app_name,
        settings.app_env,
    )
    try:
        yield
    finally:
        logger.info("application_stopped")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build an API application from explicit or environment-backed settings."""

    runtime_settings = settings or get_settings()
    application = FastAPI(
        title=runtime_settings.app_name,
        version="0.1.0",
        debug=runtime_settings.debug,
        lifespan=lifespan,
    )
    application.state.settings = runtime_settings

    @application.get(
        "/health",
        response_model=HealthResponse,
        tags=["system"],
        summary="Report backend readiness",
    )
    async def health(request: Request) -> HealthResponse:
        settings: Settings = request.app.state.settings
        return HealthResponse(
            status="ok",
            app_name=settings.app_name,
            environment=settings.app_env,
            database="configured",
        )

    return application


app = create_app()
