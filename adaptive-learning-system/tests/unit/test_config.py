"""Configuration loading tests."""

from __future__ import annotations

from pathlib import Path

import pytest


def test_settings_load_values_from_environment(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Environment variables are parsed into typed application settings."""

    database_url = f"sqlite:///{(tmp_path / 'config.db').as_posix()}"
    monkeypatch.setenv("APP_NAME", "Config Test App")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("BACKEND_PORT", "9123")
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("LLM_API_KEY", "test-key-not-real")
    monkeypatch.setenv("LLM_MODEL", "test-model-not-real")
    monkeypatch.setenv("AGENT_ENABLED", "false")

    from app.config import Settings

    settings = Settings(_env_file=None)

    assert settings.app_name == "Config Test App"
    assert settings.app_env == "test"
    assert settings.debug is False
    assert settings.backend_port == 9123
    assert settings.database_url == database_url
    assert settings.llm_api_key.get_secret_value() == "test-key-not-real"
    assert settings.llm_model == "test-model-not-real"
    assert settings.agent_enabled is False


def test_settings_accept_host_debug_mode_alias(monkeypatch) -> None:
    """A host-level DEBUG=release value maps safely to a disabled debug mode."""

    monkeypatch.setenv("DEBUG", "release")

    from app.config import Settings

    settings = Settings(_env_file=None)

    assert settings.debug is False


def test_settings_treat_host_warning_mode_as_non_debug(monkeypatch) -> None:
    """A host DEBUG=WARN logging mode must not prevent application startup."""

    monkeypatch.setenv("DEBUG", "WARN")

    from app.config import Settings

    settings = Settings(_env_file=None)

    assert settings.debug is False


def test_settings_load_values_from_dotenv(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """A caller-provided dotenv file is supported without using real secrets."""

    env_names = (
        "APP_NAME",
        "APP_ENV",
        "DEBUG",
        "DATABASE_URL",
        "LLM_API_KEY",
        "LLM_MODEL",
        "AGENT_ENABLED",
    )
    for name in env_names:
        monkeypatch.delenv(name, raising=False)

    database_url = f"sqlite:///{(tmp_path / 'dotenv.db').as_posix()}"
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text(
        "\n".join(
            (
                "APP_NAME=Dotenv Test App",
                "APP_ENV=test",
                "DEBUG=false",
                f"DATABASE_URL={database_url}",
                "LLM_API_KEY=test-key-not-real",
                "LLM_MODEL=test-model-not-real",
                "AGENT_ENABLED=false",
            )
        ),
        encoding="utf-8",
    )

    from app.config import Settings

    settings = Settings(_env_file=dotenv_path)

    assert settings.app_name == "Dotenv Test App"
    assert settings.app_env == "test"
    assert settings.debug is False
    assert settings.database_url == database_url
    assert settings.agent_enabled is False


def test_runtime_validation_names_missing_llm_settings(monkeypatch) -> None:
    """Startup validation gives actionable names without contacting an LLM."""

    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("LLM_BASE_URL", "")
    monkeypatch.setenv("LLM_MODEL", "")

    from app.config import ConfigurationError, Settings

    settings = Settings(_env_file=None)

    with pytest.raises(ConfigurationError) as exc_info:
        settings.validate_runtime_requirements()

    message = str(exc_info.value)
    assert "LLM_API_KEY" in message
    assert "LLM_BASE_URL" in message
    assert "LLM_MODEL" in message


def test_default_local_paths_are_anchored_to_project_root(
    monkeypatch,
    tmp_path: Path,
) -> None:
    """Defaults remain stable when commands run outside the project directory."""

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("UPLOAD_DIR", raising=False)
    monkeypatch.chdir(tmp_path)

    from app.config import PROJECT_ROOT, Settings

    settings = Settings(_env_file=None)
    expected_database = (PROJECT_ROOT / "data" / "app.db").resolve().as_posix()

    assert settings.database_url == f"sqlite:///{expected_database}"
    assert settings.upload_dir == (PROJECT_ROOT / "data" / "uploads").resolve()


def test_secret_value_is_redacted_from_settings_repr(monkeypatch) -> None:
    """Configuration diagnostics must not expose the provider credential."""

    secret = "never-print-this-test-secret"
    monkeypatch.setenv("LLM_API_KEY", secret)

    from app.config import Settings

    settings = Settings(_env_file=None)

    assert secret not in repr(settings)
