"""SQLAlchemy persistence model for validated Knowledge Units."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class KnowledgeUnit(Base):
    """A source-grounded unit in a document's ordered Knowledge Map."""

    __tablename__ = "knowledge_units"
    __table_args__ = (
        CheckConstraint(
            "position >= 1",
            name="ck_knowledge_units_position_positive",
        ),
        CheckConstraint(
            "estimated_reading_minutes >= 1",
            name="ck_knowledge_units_reading_minutes_positive",
        ),
        Index(
            "ix_knowledge_units_document_status",
            "document_id",
            "status",
        ),
        Index(
            "ix_knowledge_units_document_position",
            "document_id",
            "position",
            unique=True,
        ),
    )

    id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    learning_objectives: Mapped[list[str]] = mapped_column(
        "learning_objectives_json",
        JSON,
        nullable=False,
        default=list,
    )
    key_concepts: Mapped[list[str]] = mapped_column(
        "key_concepts_json",
        JSON,
        nullable=False,
        default=list,
    )
    concept_relations: Mapped[list[dict[str, str]]] = mapped_column(
        "concept_relations_json",
        JSON,
        nullable=False,
        default=list,
    )
    prerequisites: Mapped[list[str]] = mapped_column(
        "prerequisites_json",
        JSON,
        nullable=False,
        default=list,
    )
    common_misconceptions: Mapped[list[str]] = mapped_column(
        "misconceptions_json",
        JSON,
        nullable=False,
        default=list,
    )
    source_pages: Mapped[list[int]] = mapped_column(
        "source_pages_json",
        JSON,
        nullable=False,
        default=list,
    )
    estimated_reading_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="valid",
    )


__all__ = ["KnowledgeUnit"]
