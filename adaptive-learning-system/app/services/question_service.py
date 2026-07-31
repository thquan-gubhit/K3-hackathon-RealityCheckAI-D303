"""Source-grounded question generation and immutable-rubric evaluation."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.config import Settings
from app.llm.prompts import (
    build_answer_evaluation_messages,
    build_question_generation_messages,
)
from app.models.question import Question, QuestionType
from app.repositories.knowledge_unit_repository import KnowledgeUnitRepository
from app.repositories.question_repository import QuestionRepository
from app.rules.question_rules import validate_question_candidate
from app.schemas.evaluation import AnswerEvaluation, DimensionScores
from app.schemas.question import (
    MANDATORY_QUESTION_TYPES,
    QuestionBatch,
    QuestionCreate,
    QuestionRubric,
)
from app.services.source_context_service import (
    SourceContextError,
    build_unit_source_context,
)


class AssessmentServiceError(RuntimeError):
    """Recoverable assessment failure with a stable code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


class QuestionService:
    """Generate and validate Recall, Explain, and Apply questions."""

    def __init__(self, settings: Settings, *, llm_client: Any) -> None:
        self.settings = settings
        self.llm_client = llm_client

    def generate_for_unit(
        self,
        session: Session,
        knowledge_unit_id: str,
    ) -> list[Question]:
        """Idempotently ensure all three mandatory question types exist."""

        unit = KnowledgeUnitRepository(session).get(knowledge_unit_id)
        if unit is None:
            raise AssessmentServiceError(
                "KNOWLEDGE_UNIT_NOT_FOUND",
                "The requested Knowledge Unit does not exist.",
            )
        repository = QuestionRepository(session)
        existing = repository.list_for_unit(knowledge_unit_id)
        existing_types = {
            QuestionType(question.question_type) for question in existing
        }
        missing_types = [
            question_type
            for question_type in MANDATORY_QUESTION_TYPES
            if question_type not in existing_types
        ]
        if not missing_types:
            return existing

        try:
            source_context = build_unit_source_context(session, unit)
        except SourceContextError as exc:
            raise AssessmentServiceError(
                "INSUFFICIENT_CONTEXT",
                str(exc),
            ) from exc

        existing_texts = [question.question_text for question in existing]
        messages = build_question_generation_messages(
            unit=unit,
            source_context=source_context,
            existing_question_texts=existing_texts,
            candidate_count=max(
                3,
                self.settings.question_generation_candidates,
            ),
        )
        batch = self.llm_client.generate_structured(messages, QuestionBatch)
        accepted: list[QuestionCreate] = []
        for required_type in missing_types:
            for candidate in batch.candidates:
                if candidate.question_type is not required_type:
                    continue
                decision = validate_question_candidate(
                    candidate,
                    unit,  # type: ignore[arg-type]
                    existing_question_texts=[
                        *existing_texts,
                        *(payload.question_text for payload in accepted),
                    ],
                    source_text=source_context,
                )
                if not decision.accepted:
                    continue
                accepted.append(
                    QuestionCreate(
                        knowledge_unit_id=knowledge_unit_id,
                        **candidate.model_dump(
                            exclude={
                                "candidate_id",
                                "source_grounded",
                                "objective_aligned",
                                "answer_leak",
                                "ambiguous",
                                "requires_external_knowledge",
                            }
                        ),
                    )
                )
                break

        accepted_types = {payload.question_type for payload in accepted}
        still_missing = [
            question_type.value
            for question_type in missing_types
            if question_type not in accepted_types
        ]
        if still_missing:
            raise AssessmentServiceError(
                "NO_VALID_QUESTION",
                "No valid source-grounded question was produced for: "
                + ", ".join(still_missing),
            )
        repository.create_many(accepted)
        return repository.list_for_unit(knowledge_unit_id)


class EvaluationService:
    """Evaluate free text against the persisted pre-answer rubric."""

    LOW_CONFIDENCE_THRESHOLD = 0.50

    def __init__(self, settings: Settings, *, llm_client: Any) -> None:
        self.settings = settings
        self.llm_client = llm_client

    @staticmethod
    def _evaluate_choice(question: Question, selected_option: int) -> AnswerEvaluation:
        """Chấm trắc nghiệm bằng luật — không gọi LLM, không có chỗ để bịa."""

        options: list[str] = list(question.options or [])
        if not 0 <= selected_option < len(options):
            raise AssessmentServiceError(
                "INVALID_OPTION",
                "The selected option does not exist for this question.",
            )
        correct_index = int(question.correct_option or 0)
        is_correct = selected_option == correct_index
        score = 1.0 if is_correct else 0.0
        pages = ", ".join(str(page) for page in question.source_pages)
        feedback = (
            f"Chính xác. Nội dung này nằm ở trang {pages} của tài liệu."
            if is_correct
            else (
                f"Chưa đúng. Đáp án đúng là: {options[correct_index]} "
                f"— nằm ở trang {pages} của tài liệu."
            )
        )
        return AnswerEvaluation(
            overall_score=score,
            dimension_scores=DimensionScores(
                correctness=score,
                coverage=score,
                reasoning=score,
                application=score,
            ),
            correct_points=[options[correct_index]] if is_correct else [],
            missing_points=[] if is_correct else [options[correct_index]],
            incorrect_points=[] if is_correct else [options[selected_option]],
            contradictions=[],
            detected_misconceptions=[],
            feedback=feedback,
            recommended_next_action="CONTINUE" if is_correct else "REVIEW_SOURCE",
            confidence=1.0,
        )

    def evaluate(
        self,
        session: Session,
        *,
        question_id: str,
        user_answer: str | None = None,
        selected_option: int | None = None,
    ) -> AnswerEvaluation:
        """Return deterministic-score-normalized evaluation evidence."""

        question = QuestionRepository(session).get(question_id)
        if question is None:
            raise AssessmentServiceError(
                "QUESTION_NOT_FOUND",
                "The requested question does not exist.",
            )
        if question.options:
            if selected_option is None:
                raise AssessmentServiceError(
                    "OPTION_REQUIRED",
                    "This question is multiple choice; selected_option is required.",
                )
            return self._evaluate_choice(question, selected_option)
        if user_answer is None:
            raise AssessmentServiceError(
                "ANSWER_REQUIRED",
                "This question is free text; user_answer is required.",
            )
        unit = KnowledgeUnitRepository(session).get(question.knowledge_unit_id)
        if unit is None:
            raise AssessmentServiceError(
                "KNOWLEDGE_UNIT_NOT_FOUND",
                "The question's Knowledge Unit does not exist.",
            )
        try:
            source_context = build_unit_source_context(session, unit)
        except SourceContextError as exc:
            raise AssessmentServiceError(
                "INSUFFICIENT_CONTEXT",
                str(exc),
            ) from exc

        rubric = QuestionRubric.model_validate(question.rubric)
        messages = build_answer_evaluation_messages(
            question_id=question.id,
            question_text=question.question_text,
            reference_answer=question.reference_answer,
            rubric=rubric,
            source_context=source_context,
            user_answer=user_answer,
        )
        evaluation = self.llm_client.generate_structured(
            messages,
            AnswerEvaluation,
        )
        dimensions = evaluation.dimension_scores
        weights = rubric.dimension_weights
        overall_score = (
            dimensions.correctness * weights.correctness
            + dimensions.coverage * weights.coverage
            + dimensions.reasoning * weights.reasoning
            + dimensions.application * weights.application
        )
        updates: dict[str, object] = {"overall_score": overall_score}
        if evaluation.confidence < self.LOW_CONFIDENCE_THRESHOLD:
            updates.update(
                {
                    "detected_misconceptions": [],
                    "recommended_next_action": "ASK_CLARIFICATION",
                }
            )
        return evaluation.model_copy(update=updates)


__all__ = [
    "AssessmentServiceError",
    "EvaluationService",
    "QuestionService",
]
