"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from typing import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api.documents import router as documents_router
from app.api.agent import router as agent_router
from app.api.knowledge_units import router as knowledge_units_router
from app.api.learning_sessions import router as learning_sessions_router
from app.api.progress import router as progress_router
from app.config import ConfigurationError, Settings, get_settings
from app.errors import AppError
from app.llm.adapter import LLMClient
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
    if getattr(application.state, "llm_client", None) is None:
        application.state.llm_client = LLMClient(settings)
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


def create_app(
    settings: Settings | None = None,
    *,
    llm_client: object | None = None,
) -> FastAPI:
    """Build an API application from explicit or environment-backed settings."""

    runtime_settings = settings or get_settings()
    application = FastAPI(
        title=runtime_settings.app_name,
        version="0.2.0",
        debug=runtime_settings.debug,
        lifespan=lifespan,
    )
    application.state.settings = runtime_settings
    application.state.llm_client = llm_client

    @application.exception_handler(AppError)
    async def handle_app_error(
        request: Request,
        exc: AppError,
    ) -> JSONResponse:
        request_id = request.headers.get("X-Request-ID")
        logger.warning(
            "application_error code=%s status=%d path=%s",
            exc.code,
            exc.status_code,
            request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(request_id=request_id),
        )

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

    application.include_router(documents_router)
    application.include_router(knowledge_units_router)
    application.include_router(learning_sessions_router)
    application.include_router(progress_router)
    application.include_router(agent_router)
    return application


app = create_app()
