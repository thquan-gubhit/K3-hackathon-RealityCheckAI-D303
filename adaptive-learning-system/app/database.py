"""SQLAlchemy engine, session factory, and database initialization helpers."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import PROJECT_ROOT, get_settings


class Base(DeclarativeBase):
    """Declarative base shared by all application models."""


settings = get_settings()
_database_url = make_url(settings.database_url)
_connect_args = (
    {"check_same_thread": False}
    if _database_url.get_backend_name() == "sqlite"
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def _sqlite_database_path() -> Path | None:
    """Return the on-disk SQLite path, if this engine uses one."""

    database = _database_url.database
    if (
        _database_url.get_backend_name() != "sqlite"
        or not database
        or database == ":memory:"
        or database.startswith("file:")
    ):
        return None

    path = Path(database)
    return path if path.is_absolute() else (PROJECT_ROOT / path).resolve()


def init_db() -> None:
    """Create the database parent directory and all registered tables."""

    database_path = _sqlite_database_path()
    if database_path is not None:
        database_path.parent.mkdir(parents=True, exist_ok=True)

    # Import the package so future model modules exported there are registered
    # before metadata creation.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    if _database_url.get_backend_name() == "sqlite":
        with engine.begin() as connection:
            connection.exec_driver_sql("PRAGMA user_version = 1")


def get_db() -> Generator[Session, None, None]:
    """Provide a transaction-scoped SQLAlchemy session to FastAPI."""

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
