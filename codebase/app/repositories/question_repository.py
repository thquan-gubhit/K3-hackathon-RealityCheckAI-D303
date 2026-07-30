"""Persistence operations for immutable accepted questions."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.question import (
    Question,
    QuestionType,
    QuestionValidationStatus,
)
from app.rules.question_rules import question_fingerprint
from app.schemas.question import QuestionCreate


class QuestionRepository:
    """Transaction-neutral question reads and inserts."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, payload: QuestionCreate) -> Question:
        """Insert an accepted immutable question and flush its identifier."""

        record = Question(
            id=payload.id,
            knowledge_unit_id=payload.knowledge_unit_id,
            learning_objective=payload.learning_objective,
            question_type=payload.question_type.value,
            difficulty=payload.difficulty.value,
            question_text=payload.question_text,
            reference_answer=payload.reference_answer,
            rubric=payload.rubric.model_dump(mode="json"),
            source_pages=list(payload.source_pages),
            validation_status=payload.validation_status.value,
            content_fingerprint=question_fingerprint(payload.question_text),
            rubric_version=payload.rubric_version,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def create_many(
        self,
        payloads: Sequence[QuestionCreate],
    ) -> list[Question]:
        return [self.create(payload) for payload in payloads]

    def get(self, question_id: str) -> Question | None:
        return self.session.get(Question, question_id)

    def list_for_unit(
        self,
        knowledge_unit_id: str,
        *,
        accepted_only: bool = True,
    ) -> list[Question]:
        statement = select(Question).where(
            Question.knowledge_unit_id == knowledge_unit_id
        )
        if accepted_only:
            statement = statement.where(
                Question.validation_status
                == QuestionValidationStatus.ACCEPTED.value
            )
        statement = statement.order_by(Question.created_at, Question.id)
        return list(self.session.scalars(statement).all())

    def first_for_type(
        self,
        knowledge_unit_id: str,
        question_type: QuestionType,
        *,
        excluded_ids: Sequence[str] = (),
    ) -> Question | None:
        statement = (
            select(Question)
            .where(
                Question.knowledge_unit_id == knowledge_unit_id,
                Question.question_type == question_type.value,
                Question.validation_status
                == QuestionValidationStatus.ACCEPTED.value,
            )
            .order_by(Question.created_at, Question.id)
        )
        if excluded_ids:
            statement = statement.where(Question.id.not_in(excluded_ids))
        return self.session.scalar(statement)


__all__ = ["QuestionRepository"]
