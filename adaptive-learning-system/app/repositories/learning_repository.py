"""Persistence for sessions, answers, mastery, and misconceptions."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.answer import AnswerAttempt
from app.models.document import utc_now
from app.models.learning_session import LearningSession, LearningSessionStatus
from app.models.mastery import MasteryState, MasteryStatus, Misconception
from app.models.question import Question
from app.schemas.evaluation import AnswerEvaluation


class LearningRepository:
    """Transaction-neutral persistence boundary for adaptive learning."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_session(
        self,
        *,
        user_id: str,
        document_id: str,
        knowledge_unit_id: str,
    ) -> LearningSession:
        record = LearningSession(
            user_id=user_id,
            document_id=document_id,
            knowledge_unit_id=knowledge_unit_id,
            status=LearningSessionStatus.ACTIVE.value,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def get_session(self, session_id: str) -> LearningSession | None:
        return self.session.get(LearningSession, session_id)

    def set_current_question(
        self,
        session_id: str,
        question_id: str | None,
    ) -> LearningSession | None:
        record = self.get_session(session_id)
        if record is None:
            return None
        record.current_question_id = question_id
        self.session.flush()
        return record

    def increment_question_count(
        self,
        session_id: str,
        *,
        remediation: bool = False,
    ) -> LearningSession | None:
        record = self.get_session(session_id)
        if record is None:
            return None
        if remediation:
            record.remediation_question_count += 1
        else:
            record.main_question_count += 1
        self.session.flush()
        return record

    def update_session_status(
        self,
        session_id: str,
        status: LearningSessionStatus,
        *,
        completed_at: datetime | None = None,
    ) -> LearningSession | None:
        record = self.get_session(session_id)
        if record is None:
            return None
        record.status = status.value
        record.completed_at = (
            completed_at or utc_now()
            if status
            in {
                LearningSessionStatus.COMPLETED,
                LearningSessionStatus.STOPPED,
            }
            else None
        )
        self.session.flush()
        return record

    def list_attempts(self, session_id: str) -> list[AnswerAttempt]:
        statement = (
            select(AnswerAttempt)
            .where(AnswerAttempt.session_id == session_id)
            .order_by(AnswerAttempt.created_at, AnswerAttempt.id)
        )
        return list(self.session.scalars(statement).all())

    def count_question_attempts(
        self,
        session_id: str,
        question_id: str,
    ) -> int:
        statement = (
            select(func.count())
            .select_from(AnswerAttempt)
            .where(
                AnswerAttempt.session_id == session_id,
                AnswerAttempt.question_id == question_id,
            )
        )
        return int(self.session.scalar(statement) or 0)

    def count_user_question_attempts(
        self,
        *,
        user_id: str,
        question_id: str,
    ) -> int:
        """Count equivalent evidence across all sessions for this user."""

        statement = (
            select(func.count())
            .select_from(AnswerAttempt)
            .join(
                LearningSession,
                LearningSession.id == AnswerAttempt.session_id,
            )
            .where(
                LearningSession.user_id == user_id,
                AnswerAttempt.question_id == question_id,
            )
        )
        return int(self.session.scalar(statement) or 0)

    def count_answered_questions_for_unit(
        self,
        *,
        user_id: str,
        knowledge_unit_id: str,
    ) -> int:
        """Count distinct accepted question evidence for progress display."""

        statement = (
            select(func.count(func.distinct(AnswerAttempt.question_id)))
            .select_from(AnswerAttempt)
            .join(
                LearningSession,
                LearningSession.id == AnswerAttempt.session_id,
            )
            .join(Question, Question.id == AnswerAttempt.question_id)
            .where(
                LearningSession.user_id == user_id,
                Question.knowledge_unit_id == knowledge_unit_id,
            )
        )
        return int(self.session.scalar(statement) or 0)

    def create_attempt(
        self,
        *,
        session_id: str,
        question_id: str,
        user_answer: str,
        evaluation: AnswerEvaluation,
        attempt_number: int,
        evidence_weight: float,
        understanding_state: str,
        previous_mastery: float,
        new_mastery: float,
    ) -> AnswerAttempt:
        record = AnswerAttempt(
            session_id=session_id,
            question_id=question_id,
            user_answer=user_answer,
            evaluation=evaluation.model_dump(mode="json"),
            overall_score=evaluation.overall_score,
            attempt_number=attempt_number,
            evidence_weight=evidence_weight,
            understanding_state=understanding_state,
            previous_mastery=previous_mastery,
            new_mastery=new_mastery,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def get_or_create_mastery(
        self,
        *,
        user_id: str,
        knowledge_unit_id: str,
        initial_score: float,
    ) -> MasteryState:
        statement = select(MasteryState).where(
            MasteryState.user_id == user_id,
            MasteryState.knowledge_unit_id == knowledge_unit_id,
        )
        record = self.session.scalar(statement)
        if record is None:
            record = MasteryState(
                user_id=user_id,
                knowledge_unit_id=knowledge_unit_id,
                recall_score=initial_score,
                understanding_score=initial_score,
                application_score=initial_score,
                mastery_score=initial_score,
                status=MasteryStatus.NOT_STARTED.value,
            )
            self.session.add(record)
            self.session.flush()
        return record

    def list_mastery_for_user(self, user_id: str) -> list[MasteryState]:
        statement = (
            select(MasteryState)
            .where(MasteryState.user_id == user_id)
            .order_by(MasteryState.last_updated, MasteryState.id)
        )
        return list(self.session.scalars(statement).all())

    def list_misconceptions(
        self,
        *,
        user_id: str,
        knowledge_unit_id: str,
        active_only: bool = False,
    ) -> list[Misconception]:
        statement = select(Misconception).where(
            Misconception.user_id == user_id,
            Misconception.knowledge_unit_id == knowledge_unit_id,
        )
        if active_only:
            statement = statement.where(Misconception.resolved.is_(False))
        statement = statement.order_by(
            Misconception.occurrence_count.desc(),
            Misconception.concept,
        )
        return list(self.session.scalars(statement).all())

    def record_misconceptions(
        self,
        *,
        user_id: str,
        knowledge_unit_id: str,
        concepts: Sequence[str],
        severity: str = "medium",
    ) -> list[Misconception]:
        records: list[Misconception] = []
        for concept in concepts:
            statement = select(Misconception).where(
                Misconception.user_id == user_id,
                Misconception.knowledge_unit_id == knowledge_unit_id,
                func.lower(Misconception.concept) == concept.casefold(),
            )
            record = self.session.scalar(statement)
            if record is None:
                record = Misconception(
                    user_id=user_id,
                    knowledge_unit_id=knowledge_unit_id,
                    concept=concept,
                    description=concept,
                    occurrence_count=1,
                    severity=severity,
                    resolved=False,
                )
                self.session.add(record)
            else:
                record.occurrence_count += 1
                record.description = concept
                record.severity = severity
                record.resolved = False
                record.last_detected_at = utc_now()
            records.append(record)
        self.session.flush()
        return records

    def resolve_active_misconceptions(
        self,
        *,
        user_id: str,
        knowledge_unit_id: str,
    ) -> None:
        for record in self.list_misconceptions(
            user_id=user_id,
            knowledge_unit_id=knowledge_unit_id,
            active_only=True,
        ):
            record.resolved = True
        self.session.flush()


__all__ = ["LearningRepository"]
