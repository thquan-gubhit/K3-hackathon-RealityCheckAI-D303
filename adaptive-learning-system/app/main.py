"""FastAPI application entry point."""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
import re
from typing import AsyncIterator
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

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
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


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
        version="1.0.0",
        debug=runtime_settings.debug,
        lifespan=lifespan,
    )
    application.state.settings = runtime_settings
    application.state.llm_client = llm_client

    # Frontend chạy ở cổng khác (Streamlit 8501, prototype 8899) nên là
    # origin khác. Không có CORS thì trình duyệt vẫn gửi được request nhưng
    # CHẶN response — fetch ném lỗi và FE tưởng backend chết.
    application.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://(127\.0\.0\.1|localhost)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    @application.middleware("http")
    async def attach_request_id(request: Request, call_next):
        """Use a safe caller ID or generate one and echo it on every response."""

        supplied = request.headers.get("X-Request-ID", "").strip()
        request_id = (
            supplied
            if supplied and _REQUEST_ID_PATTERN.fullmatch(supplied)
            else str(uuid4())
        )
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    from app.i18n import request_language
    
    @application.middleware("http")
    async def attach_request_language(request: Request, call_next):
        lang = request.headers.get("Accept-Language", "vi")
        if not lang or lang not in ("vi", "en"):
            lang = "vi"
        
        token = request_language.set(lang)
        try:
            response = await call_next(request)
            return response
        finally:
            request_language.reset(token)

    @application.exception_handler(AppError)
    async def handle_app_error(
        request: Request,
        exc: AppError,
    ) -> JSONResponse:
        request_id = request.state.request_id
        logger.warning(
            "application_error request_id=%s code=%s status=%d path=%s",
            request_id,
            exc.code,
            exc.status_code,
            request.url.path,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(request_id=request_id),
        )

    @application.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Return stable, input-safe field locations for invalid requests."""

        request_id = request.state.request_id
        fields = [
            {
                "location": ".".join(str(part) for part in error["loc"]),
                "type": error["type"],
            }
            for error in exc.errors()
        ]
        logger.warning(
            "application_error request_id=%s code=VALIDATION_ERROR "
            "status=422 path=%s",
            request_id,
            request.url.path,
        )
        return JSONResponse(
            status_code=422,
            content=AppError(
                "VALIDATION_ERROR",
                "The request did not match the required schema.",
                status_code=422,
                details={"fields": fields},
            ).to_dict(request_id=request_id),
        )

    @application.exception_handler(StarletteHTTPException)
    async def handle_http_error(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        """Normalize framework-level route and method errors."""

        request_id = request.state.request_id
        code = (
            "ROUTE_NOT_FOUND"
            if exc.status_code == 404
            else "METHOD_NOT_ALLOWED"
            if exc.status_code == 405
            else "HTTP_ERROR"
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=AppError(
                code,
                "The requested route is unavailable."
                if exc.status_code == 404
                else "The HTTP request could not be completed.",
                status_code=exc.status_code,
            ).to_dict(request_id=request_id),
        )

    @application.exception_handler(Exception)
    async def handle_unexpected_error(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Hide exception messages while retaining safe diagnostic metadata."""

        request_id = request.state.request_id
        logger.error(
            "unhandled_application_error request_id=%s path=%s "
            "error_type=%s",
            request_id,
            request.url.path,
            type(exc).__name__,
        )
        return JSONResponse(
            status_code=500,
            content=AppError(
                "INTERNAL_SERVER_ERROR",
                "An unexpected server error occurred.",
                status_code=500,
            ).to_dict(request_id=request_id),
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
