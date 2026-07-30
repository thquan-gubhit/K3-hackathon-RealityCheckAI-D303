"""Offline, idempotent Phase 6 demo seed verification."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import build_engine
from app.models.document import Document, DocumentStatus
from app.models.knowledge_unit import KnowledgeUnit
from app.models.question import Question
from scripts.seed_demo import DEMO_DOCUMENT_ID, seed_demo


def test_demo_seed_is_complete_and_idempotent(tmp_path) -> None:
    database_url = f"sqlite:///{(tmp_path / 'seed.db').as_posix()}"

    assert seed_demo(database_url) == (3, 9)
    assert seed_demo(database_url) == (3, 9)

    engine = build_engine(database_url)
    try:
        with Session(engine) as session:
            document = session.get(Document, DEMO_DOCUMENT_ID)
            assert document is not None
            assert document.status is DocumentStatus.READY
            assert document.page_count == 3
            assert session.scalar(
                select(func.count()).select_from(KnowledgeUnit)
            ) == 3
            assert session.scalar(
                select(func.count()).select_from(Question)
            ) == 9
    finally:
        engine.dispose()
