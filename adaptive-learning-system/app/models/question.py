"""Persisted active-recall questions with immutable reference rubrics."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
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


class QuestionType(StrEnum):
    """Supported assessment and remediation question types."""

    RECALL = "recall"
    SCAFFOLDED_RECALL = "scaffolded_recall"
    EXPLAIN = "explain"
    RELATE = "relate"
    APPLY = "apply"
    APPLICATION_DIAGNOSIS = "application_diagnosis"
    MISCONCEPTION = "misconception"
    TRANSFER = "transfer"


class QuestionDifficulty(StrEnum):
    """Difficulty multiplier categories used by mastery rules."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuestionValidationStatus(StrEnum):
    """Only accepted questions may be shown to a learner."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Question(Base):
    """One source-grounded question and its pre-answer immutable rubric."""

    __tablename__ = "questions"
    __table_args__ = (
        UniqueConstraint(
            "knowledge_unit_id",
            "question_type",
            "content_fingerprint",
            name="uq_questions_unit_type_fingerprint",
        ),
        CheckConstraint(
            "rubric_version >= 1",
            name="ck_questions_rubric_version_positive",
        ),
        Index(
            "ix_questions_unit_type_status",
            "knowledge_unit_id",
            "question_type",
            "validation_status",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    knowledge_unit_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("knowledge_units.id"),
        nullable=False,
        index=True,
    )
    learning_objective: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String(32), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(16), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    reference_answer: Mapped[str] = mapped_column(Text, nullable=False)
    rubric: Mapped[dict[str, object]] = mapped_column(
        "rubric_json",
        JSON,
        nullable=False,
    )
    source_pages: Mapped[list[int]] = mapped_column(
        "source_pages_json",
        JSON,
        nullable=False,
    )
    # Trắc nghiệm (nullable): không có options nghĩa là câu tự luận.
    options: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    correct_option: Mapped[int | None] = mapped_column(Integer, nullable=True)
    validation_status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=QuestionValidationStatus.ACCEPTED.value,
    )
    content_fingerprint: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    rubric_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )


__all__ = [
    "Question",
    "QuestionDifficulty",
    "QuestionType",
    "QuestionValidationStatus",
]
