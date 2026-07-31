"""Backend launcher safeguards for local persistent storage."""

from types import SimpleNamespace

from scripts import run_backend


def test_backend_launcher_initializes_database_before_serving(monkeypatch) -> None:
    events: list[str] = []
    settings = SimpleNamespace(
        backend_host="127.0.0.1",
        backend_port=8000,
        debug=False,
        log_level="INFO",
        validate_runtime_requirements=lambda: events.append("validate"),
    )

    monkeypatch.setattr(run_backend, "get_settings", lambda: settings)
    monkeypatch.setattr(run_backend, "init_db", lambda: events.append("init_db"))
    monkeypatch.setattr(
        run_backend.uvicorn,
        "run",
        lambda *args, **kwargs: events.append("serve"),
    )

    assert run_backend.main() == 0
    assert events == ["validate", "init_db", "serve"]
