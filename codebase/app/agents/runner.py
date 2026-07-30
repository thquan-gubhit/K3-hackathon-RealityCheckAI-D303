"""Bounded Tutor Agent runner with deterministic activation and traces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from sqlalchemy.orm import Session

from app.agents.tools import TutorToolError, TutorTools
from app.config import Settings
from app.llm.prompts import build_tutor_agent_messages
from app.models.agent_trace import AgentTrace
from app.repositories.agent_trace_repository import AgentTraceRepository
from app.repositories.learning_repository import LearningRepository
from app.rules.agent_trigger_rules import (
    AgentTriggerInput,
    evaluate_agent_trigger,
)
from app.schemas.agent import AgentAction, AgentActionName


class AgentRunnerError(RuntimeError):
    """Recoverable agent policy/tool failure with a stable code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class AgentRunResult:
    run_id: str
    session_id: str
    trigger_reason: str
    status: str
    steps: tuple[AgentTrace, ...]


class TutorAgentRunner:
    """Choose only validated allow-listed actions for at most N steps."""

    TERMINAL_ACTIONS = {
        AgentActionName.FINISH_UNIT,
        AgentActionName.ESCALATE_TO_MANUAL_REVIEW,
    }

    def __init__(self, settings: Settings, *, llm_client: Any) -> None:
        self.settings = settings
        self.llm_client = llm_client

    def run(
        self,
        session: Session,
        *,
        session_id: str,
        requested_reason: str,
    ) -> AgentRunResult:
        """Evaluate policy, execute bounded tools, and persist redacted traces."""

        repository = LearningRepository(session)
        learning_session = repository.get_session(session_id)
        if learning_session is None:
            raise AgentRunnerError(
                "SESSION_NOT_FOUND",
                "The requested learning session does not exist.",
            )
        attempts = repository.list_attempts(session_id)
        mastery = repository.get_or_create_mastery(
            user_id=learning_session.user_id,
            knowledge_unit_id=learning_session.knowledge_unit_id,
            initial_score=self.settings.mastery_initial_score,
        )
        misconceptions = repository.list_misconceptions(
            user_id=learning_session.user_id,
            knowledge_unit_id=learning_session.knowledge_unit_id,
            active_only=True,
        )
        decision = evaluate_agent_trigger(
            AgentTriggerInput(
                same_misconception_count=max(
                    (item.occurrence_count for item in misconceptions),
                    default=0,
                ),
                latest_score=attempts[-1].overall_score if attempts else None,
                remediation_attempts=learning_session.remediation_question_count,
                recall_score=mastery.recall_score,
                application_score=mastery.application_score,
                explicit_request=requested_reason.upper().startswith(
                    ("EXPLICIT", "REQUEST")
                ),
            ),
            self.settings,
        )
        if decision.reason == "AGENT_DISABLED":
            raise AgentRunnerError(
                "AGENT_DISABLED",
                "Tutor Agent is disabled; use deterministic remediation.",
            )
        if not decision.activate:
            raise AgentRunnerError(
                "AGENT_NOT_ELIGIBLE",
                "Current evidence does not satisfy an agent trigger.",
            )

        run_id = str(uuid4())
        tools = TutorTools(session, learning_session)
        trace_repository = AgentTraceRepository(session)
        prior_steps: list[dict[str, object]] = []
        records: list[AgentTrace] = []
        terminal_status = "max_steps"

        for step_number in range(1, self.settings.agent_max_steps + 1):
            messages = build_tutor_agent_messages(
                scoped_context=tools.context_snapshot(),
                prior_steps=prior_steps,
            )
            action = self.llm_client.generate_structured(
                messages,
                AgentAction,
                temperature=self.settings.agent_temperature,
            )
            try:
                observation = tools.execute(action.action, action.arguments)
            except TutorToolError as exc:
                raise AgentRunnerError(
                    "AGENT_TOOL_ERROR",
                    str(exc),
                ) from exc

            is_terminal = action.stop or action.action in self.TERMINAL_ACTIONS
            is_last = step_number == self.settings.agent_max_steps
            status = (
                "completed"
                if is_terminal
                else "max_steps"
                if is_last
                else "running"
            )
            if self.settings.agent_trace_enabled:
                record = trace_repository.create(
                    run_id=run_id,
                    session_id=session_id,
                    knowledge_unit_id=learning_session.knowledge_unit_id,
                    trigger_reason=decision.reason,
                    step_number=step_number,
                    action=action,
                    observation=observation,
                    status=status,
                )
                records.append(record)
                session.commit()
            prior_steps.append(
                {
                    "step_number": step_number,
                    "action": action.action.value,
                    "observation": observation,
                    "status": status,
                }
            )
            if is_terminal:
                terminal_status = "completed"
                break
            if is_last:
                terminal_status = "max_steps"

        return AgentRunResult(
            run_id=run_id,
            session_id=session_id,
            trigger_reason=decision.reason,
            status=terminal_status,
            steps=tuple(records),
        )


__all__ = ["AgentRunResult", "AgentRunnerError", "TutorAgentRunner"]
