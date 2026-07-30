"""Database bootstrap integration tests."""

from __future__ import annotations

import importlib
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import make_url


def test_init_db_creates_and_connects_to_sqlite(
    isolated_app_environment: dict[str, str],
) -> None:
    """The configured local SQLite file is created and accepts a query."""

    from app.config import get_settings

    get_settings.cache_clear()

    import app.database as database

    database = importlib.reload(database)
    database_path = Path(
        make_url(isolated_app_environment["DATABASE_URL"]).database or ""
    )

    try:
        database.init_db()
        with database.engine.connect() as connection:
            assert connection.scalar(text("SELECT 1")) == 1
            assert connection.exec_driver_sql("PRAGMA user_version").scalar() == 1

        assert database_path.is_file()
        assert database_path.stat().st_size > 0
    finally:
        database.engine.dispose()
        get_settings.cache_clear()
