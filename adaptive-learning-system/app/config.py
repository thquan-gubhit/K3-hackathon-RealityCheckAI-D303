"""Typed application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


class ConfigurationError(RuntimeError):
    """Raised when settings are syntactically valid but cannot run the app."""

    def __init__(self, missing_variables: list[str]) -> None:
        self.missing_variables = tuple(missing_variables)
        variables = ", ".join(self.missing_variables)
        super().__init__(
            f"Missing required LLM configuration: {variables}. "
            "Copy .env.example to .env and set non-empty values before "
            "starting the backend."
        )


def _resolve_sqlite_url(value: str) -> str:
    """Anchor relative SQLite database paths to the project directory."""

    url = make_url(value)
    if url.get_backend_name() != "sqlite":
        return value

    database = url.database
    if not database or database == ":memory:" or database.startswith("file:"):
        return value

    database_path = Path(database)
    if database_path.is_absolute():
        return value

    absolute_path = (PROJECT_ROOT / database_path).resolve()
    return f"sqlite:///{absolute_path.as_posix()}"


class Settings(BaseSettings):
    """Environment-backed settings for the local MVP."""

    model_config = SettingsConfigDict(
        env_file=DEFAULT_ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )

    # Application
    app_name: str = "Adaptive Learning System"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Backend and frontend
    backend_host: str = "127.0.0.1"
    backend_port: int = Field(default=8000, ge=1, le=65535)
    frontend_host: str = "127.0.0.1"
    frontend_port: int = Field(default=8501, ge=1, le=65535)
    backend_api_url: str = ""

    # Persistence and uploads
    database_url: str = "sqlite:///./data/app.db"
    upload_dir: Path = Path("./data/uploads")
    max_upload_size_mb: int = Field(default=20, gt=0)

    # LLM provider
    llm_provider: str = "openai_compatible"
    llm_api_key: SecretStr = SecretStr("")
    llm_base_url: str = ""
    llm_model: str = ""
    llm_temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    llm_timeout_seconds: float = Field(default=60.0, gt=0)
    llm_max_retries: int = Field(default=3, ge=0)
    embedding_model: str = ""

    # Knowledge Unit rules
    ku_min_concepts: int = Field(default=2, ge=1)
    ku_max_concepts: int = Field(default=7, ge=1)
    ku_max_learning_objectives: int = Field(default=3, ge=1)
    ku_min_reading_minutes: int = Field(default=2, ge=1)
    ku_max_reading_minutes: int = Field(default=10, ge=1)
    ku_max_refinement_rounds: int = Field(default=2, ge=0)

    # Question rules
    question_count_per_unit: int = Field(default=3, ge=1)
    max_main_questions_per_unit: int = Field(default=3, ge=1)
    max_remediation_questions: int = Field(default=2, ge=0)
    question_generation_candidates: int = Field(default=5, ge=1)

    # Mastery
    mastery_initial_score: float = Field(default=0.0, ge=0.0, le=1.0)
    mastery_old_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    mastery_new_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    mastery_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    min_questions_for_mastery: int = Field(default=3, ge=1)
    require_application_for_mastery: bool = True

    # Tutor agent (implemented in a later phase)
    agent_enabled: bool = True
    agent_max_steps: int = Field(default=5, ge=1)
    agent_temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    agent_trigger_wrong_count: int = Field(default=2, ge=1)
    agent_trigger_low_score: float = Field(default=0.4, ge=0.0, le=1.0)
    agent_trigger_recall_application_gap: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
    )
    agent_trace_enabled: bool = True

    @field_validator("database_url")
    @classmethod
    def resolve_database_url(cls, value: str) -> str:
        """Resolve local SQLite URLs without changing remote database URLs."""

        return _resolve_sqlite_url(value)

    @field_validator("upload_dir")
    @classmethod
    def resolve_upload_dir(cls, value: Path) -> Path:
        """Resolve relative upload storage from the project root."""

        if value.is_absolute():
            return value
        return (PROJECT_ROOT / value).resolve()

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        """Reject misspelled log levels early."""

        normalized = value.upper()
        allowed: set[Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]] = {
            "CRITICAL",
            "ERROR",
            "WARNING",
            "INFO",
            "DEBUG",
        }
        if normalized not in allowed:
            choices = ", ".join(sorted(allowed))
            raise ValueError(f"LOG_LEVEL must be one of: {choices}")
        return normalized

    @field_validator("debug", mode="before")
    @classmethod
    def normalize_debug_aliases(cls, value: object) -> object:
        """Accept common host build-mode values without weakening validation."""

        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production"}:
                return False
            if normalized in {"debug", "development"}:
                return True
        return value

    def validate_runtime_requirements(self) -> None:
        """Fail startup clearly when mandatory LLM settings are blank."""

        missing: list[str] = []
        if not self.llm_api_key.get_secret_value().strip():
            missing.append("LLM_API_KEY")
        if not self.llm_base_url.strip():
            missing.append("LLM_BASE_URL")
        if not self.llm_model.strip():
            missing.append("LLM_MODEL")
        if missing:
            raise ConfigurationError(missing)


@lru_cache
def get_settings() -> Settings:
    """Return one immutable-in-practice settings snapshot per process."""

    return Settings()
