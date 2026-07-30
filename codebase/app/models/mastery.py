"""Persisted mastery dimensions and misconception evidence."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.document import utc_now


class MasteryStatus(StrEnum):
    """Current deterministic learning status for a user/KU pair."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    MASTERED = "mastered"


class MasteryState(Base):
    """Current score dimensions and evidence gates for one local learner."""

    __tablename__ = "mastery_states"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "knowledge_unit_id",
            name="uq_mastery_states_user_unit",
        ),
        CheckConstraint(
            "recall_score >= 0 AND recall_score <= 1",
            name="ck_mastery_states_recall",
        ),
        CheckConstraint(
            "understanding_score >= 0 AND understanding_score <= 1",
            name="ck_mastery_states_understanding",
        ),
        CheckConstraint(
            "application_score >= 0 AND application_score <= 1",
            name="ck_mastery_states_application",
        ),
        CheckConstraint(
            "mastery_score >= 0 AND mastery_score <= 1",
            name="ck_mastery_states_mastery",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    knowledge_unit_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("knowledge_units.id"),
        nullable=False,
        index=True,
    )
    recall_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    understanding_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    application_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    mastery_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=MasteryStatus.NOT_STARTED.value,
    )
    question_evidence_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    has_application_evidence: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )


class Misconception(Base):
    """Aggregated recurring misconception for a user and Knowledge Unit."""

    __tablename__ = "misconceptions"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "knowledge_unit_id",
            "concept",
            name="uq_misconceptions_user_unit_concept",
        ),
        CheckConstraint(
            "occurrence_count >= 1",
            name="ck_misconceptions_occurrence_positive",
        ),
        Index(
            "ix_misconceptions_user_unit_resolved",
            "user_id",
            "knowledge_unit_id",
            "resolved",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(String(100), nullable=False)
    knowledge_unit_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("knowledge_units.id"),
        nullable=False,
        index=True,
    )
    concept: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    occurrence_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    severity: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="medium",
    )
    resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    last_detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )


__all__ = ["MasteryState", "MasteryStatus", "Misconception"]
