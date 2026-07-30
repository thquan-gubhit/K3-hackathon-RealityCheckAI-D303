"""Read endpoints for persisted, validated Knowledge Units."""

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
from app.repositories.knowledge_unit_repository import KnowledgeUnitRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.knowledge_unit import KnowledgeUnitResponse
from app.schemas.question import (
    QuestionGenerationResponse,
    QuestionPublic,
)
from app.services.question_service import AssessmentServiceError, QuestionService


router = APIRouter(prefix="/knowledge-units", tags=["knowledge-units"])
DatabaseDependency = Annotated[Session, Depends(get_db)]


@router.get(
    "/{unit_id}",
    response_model=KnowledgeUnitResponse,
    summary="Return one Knowledge Unit",
)
def get_knowledge_unit(
    unit_id: str,
    session: DatabaseDependency,
) -> KnowledgeUnitResponse:
    unit = KnowledgeUnitRepository(session).get(unit_id)
    if unit is None:
        raise AppError(
            "KNOWLEDGE_UNIT_NOT_FOUND",
            "The requested Knowledge Unit does not exist.",
            status_code=404,
            details={"unit_id": unit_id},
        )
    return KnowledgeUnitResponse.model_validate(unit)


@router.get(
    "/{unit_id}/questions",
    response_model=list[QuestionPublic],
    summary="List learner-safe accepted questions",
)
def list_knowledge_unit_questions(
    unit_id: str,
    session: DatabaseDependency,
) -> list[QuestionPublic]:
    if KnowledgeUnitRepository(session).get(unit_id) is None:
        raise AppError(
            "KNOWLEDGE_UNIT_NOT_FOUND",
            "The requested Knowledge Unit does not exist.",
            status_code=404,
            details={"unit_id": unit_id},
        )
    return [
        QuestionPublic.model_validate(question)
        for question in QuestionRepository(session).list_for_unit(unit_id)
    ]


@router.post(
    "/{unit_id}/generate-questions",
    response_model=QuestionGenerationResponse,
    summary="Generate and persist Recall, Explain, and Apply questions",
)
def generate_knowledge_unit_questions(
    unit_id: str,
    settings: SettingsDependency,
    llm_client: LLMDependency,
    session: DatabaseDependency,
) -> QuestionGenerationResponse:
    try:
        questions = QuestionService(
            settings,
            llm_client=llm_client,
        ).generate_for_unit(session, unit_id)
        session.commit()
        return QuestionGenerationResponse(
            knowledge_unit_id=unit_id,
            questions=questions,
        )
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
            "Questions could not be saved.",
            status_code=500,
        ) from exc
