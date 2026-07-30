"""Persistence for redacted Tutor Agent activation steps."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent_trace import AgentTrace
from app.schemas.agent import AgentAction


class AgentTraceRepository:
    """Transaction-neutral trace insert and ordered reads."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        run_id: str,
        session_id: str,
        knowledge_unit_id: str,
        trigger_reason: str,
        step_number: int,
        action: AgentAction,
        observation: dict[str, object],
        status: str,
    ) -> AgentTrace:
        record = AgentTrace(
            run_id=run_id,
            session_id=session_id,
            knowledge_unit_id=knowledge_unit_id,
            trigger_reason=trigger_reason,
            step_number=step_number,
            action=action.action.value,
            reason=action.reason,
            arguments=dict(action.arguments),
            observation=observation,
            status=status,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def list_for_session(self, session_id: str) -> list[AgentTrace]:
        statement = (
            select(AgentTrace)
            .where(AgentTrace.session_id == session_id)
            .order_by(AgentTrace.created_at, AgentTrace.run_id, AgentTrace.step_number)
        )
        return list(self.session.scalars(statement).all())

    def list_for_run(self, run_id: str) -> list[AgentTrace]:
        statement = (
            select(AgentTrace)
            .where(AgentTrace.run_id == run_id)
            .order_by(AgentTrace.step_number)
        )
        return list(self.session.scalars(statement).all())


__all__ = ["AgentTraceRepository"]
