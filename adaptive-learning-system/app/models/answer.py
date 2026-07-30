"""Persisted learner answers and immutable evaluation snapshots."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.document import utc_now


class AnswerAttempt(Base):
    """One learner response evaluated against the question's stored rubric."""

    __tablename__ = "answer_attempts"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "question_id",
            "attempt_number",
            name="uq_answer_attempts_session_question_number",
        ),
        CheckConstraint(
            "overall_score >= 0 AND overall_score <= 1",
            name="ck_answer_attempts_overall_score",
        ),
        CheckConstraint(
            "attempt_number >= 1",
            name="ck_answer_attempts_number_positive",
        ),
        CheckConstraint(
            "evidence_weight > 0 AND evidence_weight <= 1",
            name="ck_answer_attempts_evidence_weight",
        ),
        Index(
            "ix_answer_attempts_session_created",
            "session_id",
            "created_at",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("learning_sessions.id"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("questions.id"),
        nullable=False,
        index=True,
    )
    user_answer: Mapped[str] = mapped_column(Text, nullable=False)
    evaluation: Mapped[dict[str, object]] = mapped_column(
        "evaluation_json",
        JSON,
        nullable=False,
    )
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    evidence_weight: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=1.0,
    )
    understanding_state: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    previous_mastery: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    new_mastery: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )


__all__ = ["AnswerAttempt"]
