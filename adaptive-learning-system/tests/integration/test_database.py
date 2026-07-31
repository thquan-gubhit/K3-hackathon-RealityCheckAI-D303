"""Database bootstrap integration tests."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.engine import make_url


def test_init_db_creates_and_connects_to_sqlite(
    isolated_app_environment: dict[str, str],
) -> None:
    """The configured local SQLite file is created and accepts a query."""

    from app.database import build_engine, init_db

    database_path = Path(
        make_url(isolated_app_environment["DATABASE_URL"]).database or ""
    )
    engine = build_engine(isolated_app_environment["DATABASE_URL"])

    try:
        init_db(engine)
        with engine.connect() as connection:
            assert connection.scalar(text("SELECT 1")) == 1
            assert connection.exec_driver_sql("PRAGMA user_version").scalar() == 5
        assert {
            "documents",
            "document_pages",
            "knowledge_units",
            "questions",
            "learning_sessions",
            "answer_attempts",
            "mastery_states",
            "misconceptions",
            "agent_traces",
        }.issubset(inspect(engine).get_table_names())

        assert database_path.is_file()
        assert database_path.stat().st_size > 0
    finally:
        engine.dispose()
