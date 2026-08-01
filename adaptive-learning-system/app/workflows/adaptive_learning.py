"""Deterministic session, evaluation, mastery, and next-action workflow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.config import Settings
from app.models.answer import AnswerAttempt
from app.models.document import DocumentStatus, utc_now
from app.models.knowledge_unit import KnowledgeUnit
from app.models.learning_session import LearningSession, LearningSessionStatus
from app.models.mastery import MasteryState, MasteryStatus, Misconception
from app.models.question import Question, QuestionDifficulty, QuestionType
from app.repositories.document_repository import DocumentRepository
from app.repositories.knowledge_unit_repository import KnowledgeUnitRepository
from app.repositories.learning_repository import LearningRepository
from app.repositories.question_repository import QuestionRepository
from app.rules.mastery_rules import (
    calculate_mastery,
    derive_mastery_status,
    understanding_state,
    update_dimension,
)
from app.rules.question_rules import (
    LearningEvidence,
    QuestionRoute,
    select_next_question,
)
from app.schemas.evaluation import AnswerEvaluation
from app.schemas.learning import LearningSessionCreate
from app.services.question_service import EvaluationService, QuestionService


class LearningWorkflowError(RuntimeError):
    """Recoverable adaptive workflow error with a stable code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class NextQuestionResult:
    session: LearningSession
    question: Question | None
    route: QuestionRoute


@dataclass(frozen=True, slots=True)
class AnswerWorkflowResult:
    attempt: AnswerAttempt
    evaluation: AnswerEvaluation
    mastery: MasteryState
    misconceptions: tuple[Misconception, ...]
    next_action: str


@dataclass(frozen=True, slots=True)
class ProgressUnit:
    unit: KnowledgeUnit
    mastery: MasteryState
    answered_questions: int
    active_misconceptions: tuple[Misconception, ...]


class AdaptiveLearningWorkflow:
    """Coordinate normal learning without delegating it to the Tutor Agent."""

    def __init__(self, settings: Settings, *, llm_client: Any) -> None:
        self.settings = settings
        self.llm_client = llm_client

    def create_session(
        self,
        session: Session,
        payload: LearningSessionCreate,
    ) -> LearningSession:
        """Validate a ready map, ensure questions, and start one session."""

        document = DocumentRepository(session).get(payload.document_id)
        if document is None:
            raise LearningWorkflowError(
                "DOCUMENT_NOT_FOUND",
                "The requested document does not exist.",
            )
        if document.status is not DocumentStatus.READY:
            raise LearningWorkflowError(
                "DOCUMENT_NOT_READY",
                "Process the document before starting a learning session.",
            )

        unit_repository = KnowledgeUnitRepository(session)
        if payload.knowledge_unit_id is None:
            units = unit_repository.list_for_document(payload.document_id)
            unit = units[0] if units else None
        else:
            unit = unit_repository.get(payload.knowledge_unit_id)
        if unit is None or unit.document_id != payload.document_id:
            raise LearningWorkflowError(
                "KNOWLEDGE_UNIT_NOT_FOUND",
                "The requested Knowledge Unit is not part of this document.",
            )

        QuestionService(
            self.settings,
            llm_client=self.llm_client,
        ).generate_for_unit(session, unit.id)
        repository = LearningRepository(session)
        repository.get_or_create_mastery(
            user_id=payload.user_id,
            knowledge_unit_id=unit.id,
            initial_score=self.settings.mastery_initial_score,
        )
        return repository.create_session(
            user_id=payload.user_id,
            document_id=document.id,
            knowledge_unit_id=unit.id,
        )

    def next_question(
        self,
        session: Session,
        session_id: str,
    ) -> NextQuestionResult:
        """Select the next normal activity from persisted evidence."""

        repository = LearningRepository(session)
        learning_session = repository.get_session(session_id)
        if learning_session is None:
            raise LearningWorkflowError(
                "SESSION_NOT_FOUND",
                "The requested learning session does not exist.",
            )
        if learning_session.status in {
            LearningSessionStatus.COMPLETED.value,
            LearningSessionStatus.STOPPED.value,
        }:
            raise LearningWorkflowError(
                "SESSION_NOT_ACTIVE",
                "The learning session is already finished.",
            )
        if learning_session.current_question_id:
            current = QuestionRepository(session).get(
                learning_session.current_question_id
            )
            if current is not None:
                return NextQuestionResult(
                    learning_session,
                    current,
                    QuestionRoute(
                        next_action="ASK_QUESTION",
                        question_type=QuestionType(current.question_type),
                        rule_id="QS-CURRENT-001",
                        reason="Return the unanswered selected question.",
                    ),
                )

        attempts = repository.list_attempts(session_id)
        mastery = repository.get_or_create_mastery(
            user_id=learning_session.user_id,
            knowledge_unit_id=learning_session.knowledge_unit_id,
            initial_score=self.settings.mastery_initial_score,
        )
        active_misconceptions = repository.list_misconceptions(
            user_id=learning_session.user_id,
            knowledge_unit_id=learning_session.knowledge_unit_id,
            active_only=True,
        )
        latest_recall_score: float | None = None
        for attempt in reversed(attempts):
            question = QuestionRepository(session).get(attempt.question_id)
            if question is not None and question.question_type == QuestionType.RECALL.value:
                latest_recall_score = attempt.overall_score
                break
        evidence = LearningEvidence(
            answered_questions=len({attempt.question_id for attempt in attempts}),
            main_question_count=learning_session.main_question_count,
            remediation_question_count=(
                learning_session.remediation_question_count
            ),
            latest_score=attempts[-1].overall_score if attempts else None,
            latest_recall_score=latest_recall_score,
            recall_score=mastery.recall_score,
            application_score=mastery.application_score,
            same_misconception_count=max(
                (
                    misconception.occurrence_count
                    for misconception in active_misconceptions
                ),
                default=0,
            ),
        )
        route = select_next_question(evidence, self.settings)

        if route.next_action == "ACTIVATE_TUTOR_AGENT":
            if self.settings.agent_enabled:
                return NextQuestionResult(learning_session, None, route)
            return self._deterministic_remediation(
                session,
                repository,
                learning_session,
                reason="Tutor Agent is disabled; use bounded remediation.",
            )
        if route.next_action == "FINISH_OR_REMEDIATE":
            if mastery.status == MasteryStatus.MASTERED.value:
                repository.update_session_status(
                    session_id,
                    LearningSessionStatus.COMPLETED,
                )
                return NextQuestionResult(
                    learning_session,
                    None,
                    QuestionRoute(
                        "FINISH_UNIT",
                        None,
                        "QS-FINISH-001",
                        "Mastery requirements are satisfied.",
                    ),
                )
            return self._deterministic_remediation(
                session,
                repository,
                learning_session,
                reason="Main-question cap reached without mastery.",
            )

        question_repository = QuestionRepository(session)
        answered_ids = list({attempt.question_id for attempt in attempts})
        question = (
            question_repository.first_for_type(
                learning_session.knowledge_unit_id,
                route.question_type or QuestionType.RECALL,
                excluded_ids=answered_ids,
            )
            if route.question_type is not None
            else None
        )
        if question is None:
            question = next(
                (
                    candidate
                    for candidate in question_repository.list_for_unit(
                        learning_session.knowledge_unit_id
                    )
                    if candidate.id not in answered_ids
                ),
                None,
            )
        if question is None:
            return self._deterministic_remediation(
                session,
                repository,
                learning_session,
                reason="No unused main question remains.",
            )
        repository.set_current_question(session_id, question.id)
        return NextQuestionResult(learning_session, question, route)

    def submit_answer(
        self,
        session: Session,
        *,
        session_id: str,
        question_id: str,
        user_answer: str | None = None,
    ) -> AnswerWorkflowResult:
        """Evaluate and atomically update attempt, mastery, and misconceptions."""

        repository = LearningRepository(session)
        learning_session = repository.get_session(session_id)
        if learning_session is None:
            raise LearningWorkflowError(
                "SESSION_NOT_FOUND",
                "The requested learning session does not exist.",
            )
        if learning_session.current_question_id != question_id:
            raise LearningWorkflowError(
                "QUESTION_NOT_SELECTED",
                "Request the next question before submitting an answer.",
            )
        question = QuestionRepository(session).get(question_id)
        if (
            question is None
            or question.knowledge_unit_id != learning_session.knowledge_unit_id
        ):
            raise LearningWorkflowError(
                "QUESTION_NOT_FOUND",
                "The selected question does not belong to this session.",
            )

        evaluation = EvaluationService(
            self.settings,
            llm_client=self.llm_client,
        ).evaluate(
            session,
            question_id=question_id,
            user_answer=user_answer,
        )
        prior_user_attempts = repository.count_user_question_attempts(
            user_id=learning_session.user_id,
            question_id=question_id,
        )
        attempt_number = prior_user_attempts + 1
        mastery = repository.get_or_create_mastery(
            user_id=learning_session.user_id,
            knowledge_unit_id=learning_session.knowledge_unit_id,
            initial_score=self.settings.mastery_initial_score,
        )
        previous_mastery = mastery.mastery_score
        calculation = calculate_mastery(
            old_mastery=previous_mastery,
            answer_score=evaluation.overall_score,
            difficulty=QuestionDifficulty(question.difficulty),
            attempt_number=attempt_number,
            settings=self.settings,
        )
        dimensions = evaluation.dimension_scores
        if question.question_type in {
            QuestionType.RECALL.value,
            QuestionType.SCAFFOLDED_RECALL.value,
        }:
            mastery.recall_score = update_dimension(
                mastery.recall_score,
                dimensions.correctness,
                evidence=calculation.evidence_weight,
                settings=self.settings,
            )
        elif question.question_type == QuestionType.EXPLAIN.value:
            mastery.understanding_score = update_dimension(
                mastery.understanding_score,
                (dimensions.coverage + dimensions.reasoning) / 2,
                evidence=calculation.evidence_weight,
                settings=self.settings,
            )
        elif question.question_type in {
            QuestionType.APPLY.value,
            QuestionType.APPLICATION_DIAGNOSIS.value,
            QuestionType.TRANSFER.value,
        }:
            mastery.application_score = update_dimension(
                mastery.application_score,
                dimensions.application,
                evidence=calculation.evidence_weight,
                settings=self.settings,
            )
            if evaluation.overall_score >= 0.60:
                mastery.has_application_evidence = True

        mastery.mastery_score = calculation.new_mastery
        if prior_user_attempts == 0:
            mastery.question_evidence_count += 1
        if evaluation.detected_misconceptions:
            repository.record_misconceptions(
                user_id=learning_session.user_id,
                knowledge_unit_id=learning_session.knowledge_unit_id,
                concepts=evaluation.detected_misconceptions,
                severity="medium",
            )
        elif evaluation.overall_score >= 0.75:
            repository.resolve_active_misconceptions(
                user_id=learning_session.user_id,
                knowledge_unit_id=learning_session.knowledge_unit_id,
            )

        active = repository.list_misconceptions(
            user_id=learning_session.user_id,
            knowledge_unit_id=learning_session.knowledge_unit_id,
            active_only=True,
        )
        mastery.status = derive_mastery_status(
            mastery_score=mastery.mastery_score,
            question_evidence_count=mastery.question_evidence_count,
            has_application_evidence=mastery.has_application_evidence,
            has_critical_misconception=any(
                misconception.severity == "critical"
                for misconception in active
            ),
            settings=self.settings,
        ).value
        mastery.last_updated = utc_now()

        remediation = (
            learning_session.main_question_count
            >= self.settings.max_main_questions_per_unit
        )
        repository.increment_question_count(
            session_id,
            remediation=remediation,
        )
        if evaluation.recommended_next_action != "ASK_CLARIFICATION":
            repository.set_current_question(session_id, None)
        attempt = repository.create_attempt(
            session_id=session_id,
            question_id=question_id,
            user_answer=user_answer or "",
            evaluation=evaluation,
            attempt_number=attempt_number,
            evidence_weight=calculation.evidence_weight,
            understanding_state=understanding_state(
                evaluation.overall_score
            ).value,
            previous_mastery=previous_mastery,
            new_mastery=mastery.mastery_score,
        )

        max_occurrences = max(
            (misconception.occurrence_count for misconception in active),
            default=0,
        )
        if mastery.status == MasteryStatus.MASTERED.value:
            next_action = "FINISH_UNIT"
        elif max_occurrences >= self.settings.agent_trigger_wrong_count:
            next_action = (
                "ACTIVATE_TUTOR_AGENT"
                if self.settings.agent_enabled
                else "DETERMINISTIC_REMEDIATION"
            )
        else:
            next_action = evaluation.recommended_next_action
        return AnswerWorkflowResult(
            attempt=attempt,
            evaluation=evaluation,
            mastery=mastery,
            misconceptions=tuple(active),
            next_action=next_action,
        )

    def finish_unit(
        self,
        session: Session,
        session_id: str,
    ) -> LearningSession:
        """Finish only after mastery or the bounded main loop."""

        repository = LearningRepository(session)
        learning_session = repository.get_session(session_id)
        if learning_session is None:
            raise LearningWorkflowError(
                "SESSION_NOT_FOUND",
                "The requested learning session does not exist.",
            )
        mastery = repository.get_or_create_mastery(
            user_id=learning_session.user_id,
            knowledge_unit_id=learning_session.knowledge_unit_id,
            initial_score=self.settings.mastery_initial_score,
        )
        if (
            mastery.status != MasteryStatus.MASTERED.value
            and learning_session.main_question_count
            < self.settings.max_main_questions_per_unit
        ):
            raise LearningWorkflowError(
                "UNIT_NOT_FINISHABLE",
                "Complete the main question loop before finishing this unit.",
            )
        updated = repository.update_session_status(
            session_id,
            LearningSessionStatus.COMPLETED,
        )
        assert updated is not None
        return updated

    def progress_for_user(
        self,
        session: Session,
        user_id: str,
    ) -> list[ProgressUnit]:
        """Return every valid KU with a persisted default/current mastery row."""

        repository = LearningRepository(session)
        progress: list[ProgressUnit] = []
        for unit in KnowledgeUnitRepository(session).list_all():
            mastery = repository.get_or_create_mastery(
                user_id=user_id,
                knowledge_unit_id=unit.id,
                initial_score=self.settings.mastery_initial_score,
            )
            progress.append(
                ProgressUnit(
                    unit=unit,
                    mastery=mastery,
                    answered_questions=(
                        repository.count_answered_questions_for_unit(
                            user_id=user_id,
                            knowledge_unit_id=unit.id,
                        )
                    ),
                    active_misconceptions=tuple(
                        repository.list_misconceptions(
                            user_id=user_id,
                            knowledge_unit_id=unit.id,
                            active_only=True,
                        )
                    ),
                )
            )
        return progress

    def _deterministic_remediation(
        self,
        session: Session,
        repository: LearningRepository,
        learning_session: LearningSession,
        *,
        reason: str,
    ) -> NextQuestionResult:
        if (
            learning_session.remediation_question_count
            >= self.settings.max_remediation_questions
        ):
            repository.update_session_status(
                learning_session.id,
                LearningSessionStatus.NEEDS_REMEDIATION,
            )
            return NextQuestionResult(
                learning_session,
                None,
                QuestionRoute(
                    "FINISH_OR_REVIEW",
                    None,
                    "QS-REMEDIATE-LIMIT-001",
                    "The remediation limit has been reached.",
                ),
            )
        question = QuestionRepository(session).first_for_type(
            learning_session.knowledge_unit_id,
            QuestionType.RECALL,
        )
        if question is None:
            raise LearningWorkflowError(
                "NO_NEXT_ACTIVITY",
                "No remediation question is available.",
            )
        repository.set_current_question(learning_session.id, question.id)
        return NextQuestionResult(
            learning_session,
            question,
            QuestionRoute(
                "DETERMINISTIC_REMEDIATION",
                QuestionType.RECALL,
                "QS-REMEDIATE-001",
                reason,
            ),
        )


__all__ = [
    "AdaptiveLearningWorkflow",
    "AnswerWorkflowResult",
    "LearningWorkflowError",
    "NextQuestionResult",
    "ProgressUnit",
]
