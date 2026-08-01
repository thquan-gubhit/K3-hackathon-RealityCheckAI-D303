"""Learning session, next-question, answer, and finish endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import LLMDependency, SettingsDependency
from app.api.error_mapping import assessment_app_error
from app.database import get_db
from app.errors import AppError
from app.llm import InvalidLLMOutputError, LLMProviderError, LLMTimeoutError
from app.repositories.learning_repository import LearningRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.evaluation import AnswerSubmission
from app.schemas.learning import (
    AnswerResultResponse,
    LearningSessionCreate,
    LearningSessionRead,
    NextQuestionResponse,
)
from app.services.question_service import AssessmentServiceError
from app.workflows.adaptive_learning import (
    AdaptiveLearningWorkflow,
    LearningWorkflowError,
)


router = APIRouter(prefix="/learning-sessions", tags=["learning-sessions"])
DatabaseDependency = Annotated[Session, Depends(get_db)]


def _learning_app_error(exc: LearningWorkflowError) -> AppError:
    not_found = {
        "DOCUMENT_NOT_FOUND",
        "KNOWLEDGE_UNIT_NOT_FOUND",
        "QUESTION_NOT_FOUND",
        "SESSION_NOT_FOUND",
    }
    conflict = {
        "DOCUMENT_NOT_READY",
        "QUESTION_NOT_SELECTED",
        "SESSION_NOT_ACTIVE",
        "UNIT_NOT_FINISHABLE",
    }
    status = 404 if exc.code in not_found else 409 if exc.code in conflict else 422
    return AppError(exc.code, str(exc), status_code=status)


@router.post(
    "",
    response_model=LearningSessionRead,
    status_code=201,
    summary="Start a Knowledge Unit learning session",
)
def create_learning_session(
    payload: LearningSessionCreate,
    settings: SettingsDependency,
    llm_client: LLMDependency,
    session: DatabaseDependency,
) -> LearningSessionRead:
    try:
        record = AdaptiveLearningWorkflow(
            settings,
            llm_client=llm_client,
        ).create_session(session, payload)
        session.commit()
        return LearningSessionRead.model_validate(record)
    except LearningWorkflowError as exc:
        session.rollback()
        raise _learning_app_error(exc) from exc
    except (
        AssessmentServiceError,
        InvalidLLMOutputError,
        LLMProviderError,
        LLMTimeoutError,
    ) as exc:
        session.rollback()
        raise assessment_app_error(exc) from exc
    except SQLAlchemyError as exc:
        session.rollback()
        raise AppError(
            "DATABASE_ERROR",
            "The learning session could not be created.",
            status_code=500,
        ) from exc


@router.get(
    "/{session_id}",
    response_model=LearningSessionRead,
    summary="Return learning session state",
)
def get_learning_session(
    session_id: str,
    session: DatabaseDependency,
) -> LearningSessionRead:
    record = LearningRepository(session).get_session(session_id)
    if record is None:
        raise AppError(
            "SESSION_NOT_FOUND",
            "The requested learning session does not exist.",
            status_code=404,
        )
    return LearningSessionRead.model_validate(record)


@router.get(
    "/{session_id}/next-question",
    response_model=NextQuestionResponse,
    summary="Select the next activity using deterministic rules",
)
def get_next_question(
    session_id: str,
    settings: SettingsDependency,
    llm_client: LLMDependency,
    session: DatabaseDependency,
) -> NextQuestionResponse:
    try:
        result = AdaptiveLearningWorkflow(
            settings,
            llm_client=llm_client,
        ).next_question(session, session_id)
        session.commit()
        return NextQuestionResponse(
            session=result.session,
            question=result.question,
            route_reason=result.route.reason,
            next_action=result.route.next_action,
        )
    except LearningWorkflowError as exc:
        session.rollback()
        raise _learning_app_error(exc) from exc
    except SQLAlchemyError as exc:
        session.rollback()
        raise AppError(
            "DATABASE_ERROR",
            "The next activity could not be selected.",
            status_code=500,
        ) from exc


@router.post(
    "/{session_id}/answers",
    response_model=AnswerResultResponse,
    summary="Evaluate an answer and update mastery atomically",
)
def submit_answer(
    session_id: str,
    payload: AnswerSubmission,
    settings: SettingsDependency,
    llm_client: LLMDependency,
    session: DatabaseDependency,
) -> AnswerResultResponse:
    try:
        result = AdaptiveLearningWorkflow(
            settings,
            llm_client=llm_client,
        ).submit_answer(
            session,
            session_id=session_id,
            question_id=payload.question_id,
            user_answer=payload.user_answer,
        )
        session.commit()
        # Chỉ lộ đáp án tham chiếu SAU khi học viên đã nộp bài.
        question = QuestionRepository(session).get(payload.question_id)
        return AnswerResultResponse(
            attempt=result.attempt,
            evaluation=result.evaluation,
            mastery=result.mastery,
            misconceptions=list(result.misconceptions),
            next_action=result.next_action,
            reference_answer=question.reference_answer if question else None,
        )
    except LearningWorkflowError as exc:
        session.rollback()
        raise _learning_app_error(exc) from exc
    except (
        AssessmentServiceError,
        InvalidLLMOutputError,
        LLMProviderError,
        LLMTimeoutError,
    ) as exc:
        session.rollback()
        raise assessment_app_error(exc) from exc
    except SQLAlchemyError as exc:
        session.rollback()
        raise AppError(
            "DATABASE_ERROR",
            "The answer and mastery update could not be saved.",
            status_code=500,
        ) from exc


@router.post(
    "/{session_id}/finish-unit",
    response_model=LearningSessionRead,
    summary="Finish a unit after deterministic gates",
)
def finish_unit(
    session_id: str,
    settings: SettingsDependency,
    llm_client: LLMDependency,
    session: DatabaseDependency,
) -> LearningSessionRead:
    try:
        record = AdaptiveLearningWorkflow(
            settings,
            llm_client=llm_client,
        ).finish_unit(session, session_id)
        session.commit()
        return LearningSessionRead.model_validate(record)
    except LearningWorkflowError as exc:
        session.rollback()
        raise _learning_app_error(exc) from exc
    except SQLAlchemyError as exc:
        session.rollback()
        raise AppError(
            "DATABASE_ERROR",
            "The unit could not be finished.",
            status_code=500,
        ) from exc
