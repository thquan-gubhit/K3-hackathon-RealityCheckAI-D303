"""Aggregate and per-Knowledge-Unit progress endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import SettingsDependency
from app.database import get_db
from app.errors import AppError
from app.models.mastery import MasteryStatus
from app.schemas.learning import ProgressUnitResponse, UserProgressResponse
from app.workflows.adaptive_learning import AdaptiveLearningWorkflow


router = APIRouter(prefix="/progress", tags=["progress"])
DatabaseDependency = Annotated[Session, Depends(get_db)]


def _progress_item(item) -> ProgressUnitResponse:
    return ProgressUnitResponse(
        knowledge_unit_id=item.unit.id,
        title=item.unit.title,
        position=item.unit.position,
        mastery=item.mastery,
        answered_questions=item.answered_questions,
        active_misconceptions=list(item.active_misconceptions),
    )


@router.get(
    "/{user_id}",
    response_model=UserProgressResponse,
    summary="Return progress across all Knowledge Units",
)
def get_user_progress(
    user_id: str,
    settings: SettingsDependency,
    session: DatabaseDependency,
) -> UserProgressResponse:
    try:
        items = AdaptiveLearningWorkflow(
            settings,
            llm_client=object(),
        ).progress_for_user(session, user_id)
        session.commit()
    except SQLAlchemyError as exc:
        session.rollback()
        raise AppError(
            "DATABASE_ERROR",
            "Progress could not be loaded.",
            status_code=500,
        ) from exc
    recommended = next(
        (
            item.unit.id
            for item in items
            if item.mastery.status != MasteryStatus.MASTERED.value
        ),
        None,
    )
    return UserProgressResponse(
        user_id=user_id,
        knowledge_units=[_progress_item(item) for item in items],
        recommended_next_unit_id=recommended,
    )


@router.get(
    "/{user_id}/knowledge-units/{unit_id}",
    response_model=ProgressUnitResponse,
    summary="Return progress for one Knowledge Unit",
)
def get_unit_progress(
    user_id: str,
    unit_id: str,
    settings: SettingsDependency,
    session: DatabaseDependency,
) -> ProgressUnitResponse:
    try:
        items = AdaptiveLearningWorkflow(
            settings,
            llm_client=object(),
        ).progress_for_user(session, user_id)
        item = next(
            (candidate for candidate in items if candidate.unit.id == unit_id),
            None,
        )
        session.commit()
    except SQLAlchemyError as exc:
        session.rollback()
        raise AppError(
            "DATABASE_ERROR",
            "Progress could not be loaded.",
            status_code=500,
        ) from exc
    if item is None:
        raise AppError(
            "MASTERY_NOT_FOUND",
            "The requested Knowledge Unit progress does not exist.",
            status_code=404,
        )
    return _progress_item(item)
