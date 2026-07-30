"""SQLAlchemy engine, session factory, and database initialization helpers."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import PROJECT_ROOT, get_settings


class Base(DeclarativeBase):
    """Declarative base shared by all application models."""


def build_engine(database_url: str) -> Engine:
    """Create an engine with safe SQLite defaults when applicable."""

    parsed_url = make_url(database_url)
    connect_args = (
        {"check_same_thread": False}
        if parsed_url.get_backend_name() == "sqlite"
        else {}
    )
    database_engine = create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )

    if parsed_url.get_backend_name() == "sqlite":

        @event.listens_for(database_engine, "connect")
        def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("PRAGMA foreign_keys=ON")
            finally:
                cursor.close()

    return database_engine


def build_session_factory(
    database_engine: Engine,
) -> sessionmaker[Session]:
    """Create a session factory for an explicit engine."""

    return sessionmaker(
        bind=database_engine,
        class_=Session,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


settings = get_settings()
engine = build_engine(settings.database_url)
SessionLocal = build_session_factory(engine)


def _sqlite_database_path(database_engine: Engine = engine) -> Path | None:
    """Return the on-disk SQLite path, if the engine uses one."""

    parsed_url = database_engine.url
    database = parsed_url.database
    if (
        parsed_url.get_backend_name() != "sqlite"
        or not database
        or database == ":memory:"
        or database.startswith("file:")
    ):
        return None

    path = Path(database)
    return path if path.is_absolute() else (PROJECT_ROOT / path).resolve()


def init_db(database_engine: Engine = engine) -> None:
    """Create the database parent directory and all registered tables."""

    database_path = _sqlite_database_path(database_engine)
    if database_path is not None:
        database_path.parent.mkdir(parents=True, exist_ok=True)

    # Import the package so future model modules exported there are registered
    # before metadata creation.
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=database_engine)
    if database_engine.url.get_backend_name() == "sqlite":
        with database_engine.begin() as connection:
            connection.exec_driver_sql("PRAGMA user_version = 5")


def get_db() -> Generator[Session, None, None]:
    """Provide a transaction-scoped SQLAlchemy session to FastAPI."""

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
