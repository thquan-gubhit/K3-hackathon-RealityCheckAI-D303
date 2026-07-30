"""Persisted local-user learning sessions."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.document import utc_now


class LearningSessionStatus(StrEnum):
    """Lifecycle of one focused Knowledge Unit study session."""

    ACTIVE = "active"
    COMPLETED = "completed"
    NEEDS_REMEDIATION = "needs_remediation"
    STOPPED = "stopped"


class LearningSession(Base):
    """Local learner progress through one document and Knowledge Unit."""

    __tablename__ = "learning_sessions"
    __table_args__ = (
        CheckConstraint(
            "main_question_count >= 0",
            name="ck_learning_sessions_main_count",
        ),
        CheckConstraint(
            "remediation_question_count >= 0",
            name="ck_learning_sessions_remediation_count",
        ),
        Index(
            "ix_learning_sessions_user_status_started",
            "user_id",
            "status",
            "started_at",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="local-user",
    )
    document_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )
    knowledge_unit_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("knowledge_units.id"),
        nullable=False,
        index=True,
    )
    current_question_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("questions.id"),
        nullable=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=LearningSessionStatus.ACTIVE.value,
    )
    main_question_count: Mapped[int] = mapped_column(nullable=False, default=0)
    remediation_question_count: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )


__all__ = ["LearningSession", "LearningSessionStatus"]
