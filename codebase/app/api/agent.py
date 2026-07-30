"""Tutor Agent run and trace endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.agents.runner import AgentRunnerError, TutorAgentRunner
from app.api.dependencies import LLMDependency, SettingsDependency
from app.api.error_mapping import assessment_app_error
from app.database import get_db
from app.errors import AppError
from app.llm import InvalidLLMOutputError, LLMProviderError, LLMTimeoutError
from app.repositories.agent_trace_repository import AgentTraceRepository
from app.repositories.learning_repository import LearningRepository
from app.schemas.agent import (
    AgentRunRequest,
    AgentRunResponse,
    AgentTraceRead,
)


router = APIRouter(tags=["tutor-agent"])
DatabaseDependency = Annotated[Session, Depends(get_db)]


def _agent_app_error(exc: AgentRunnerError) -> AppError:
    if exc.code == "SESSION_NOT_FOUND":
        status = 404
    elif exc.code in {"AGENT_DISABLED", "AGENT_NOT_ELIGIBLE"}:
        status = 409
    else:
        status = 422
    return AppError(exc.code, str(exc), status_code=status)


@router.post(
    "/learning-sessions/{session_id}/agent/run",
    response_model=AgentRunResponse,
    summary="Run the bounded Tutor Agent when policy permits",
)
def run_tutor_agent(
    session_id: str,
    payload: AgentRunRequest,
    settings: SettingsDependency,
    llm_client: LLMDependency,
    session: DatabaseDependency,
) -> AgentRunResponse:
    try:
        result = TutorAgentRunner(
            settings,
            llm_client=llm_client,
        ).run(
            session,
            session_id=session_id,
            requested_reason=payload.reason,
        )
        session.commit()
        return AgentRunResponse(
            run_id=result.run_id,
            session_id=result.session_id,
            trigger_reason=result.trigger_reason,
            status=result.status,
            steps=list(result.steps),
        )
    except AgentRunnerError as exc:
        session.rollback()
        raise _agent_app_error(exc) from exc
    except (
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
            "Tutor Agent traces could not be saved.",
            status_code=500,
        ) from exc


@router.get(
    "/learning-sessions/{session_id}/agent/traces",
    response_model=list[AgentTraceRead],
    summary="Return redacted Tutor Agent traces",
)
def get_tutor_agent_traces(
    session_id: str,
    session: DatabaseDependency,
) -> list[AgentTraceRead]:
    if LearningRepository(session).get_session(session_id) is None:
        raise AppError(
            "SESSION_NOT_FOUND",
            "The requested learning session does not exist.",
            status_code=404,
        )
    return [
        AgentTraceRead.model_validate(record)
        for record in AgentTraceRepository(session).list_for_session(session_id)
    ]
