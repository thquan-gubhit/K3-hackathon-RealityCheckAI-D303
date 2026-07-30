"""Validated Tutor Agent actions, runs, and redacted trace responses."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgentActionName(StrEnum):
    """Complete allow-list of actions the model may request."""

    GET_CURRENT_UNIT = "get_current_unit"
    GET_USER_MASTERY = "get_user_mastery"
    GET_ANSWER_HISTORY = "get_answer_history"
    GET_DETECTED_MISCONCEPTIONS = "get_detected_misconceptions"
    GET_PREREQUISITE_UNITS = "get_prerequisite_units"
    GENERATE_SCAFFOLDED_QUESTION = "generate_scaffolded_question"
    GIVE_HINT = "give_hint"
    GIVE_EXPLANATION = "give_explanation"
    FINISH_UNIT = "finish_unit"
    ESCALATE_TO_MANUAL_REVIEW = "escalate_to_manual_review"


class AgentAction(BaseModel):
    """One schema-valid operational action, never private reasoning."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    reason: str = Field(min_length=1, max_length=500)
    action: AgentActionName
    arguments: dict[str, Any] = Field(default_factory=dict)
    stop: bool = False


class AgentRunRequest(BaseModel):
    """Request activation with a transport-safe reason."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    reason: str = Field(
        default="EXPLICIT_DIFFERENT_EXPLANATION",
        min_length=1,
        max_length=100,
    )


class AgentTraceRead(BaseModel):
    """Redacted persisted trace step."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    run_id: str
    session_id: str
    knowledge_unit_id: str
    trigger_reason: str
    step_number: int = Field(ge=1)
    action: AgentActionName
    reason: str
    arguments: dict[str, Any]
    observation: dict[str, Any]
    status: str
    created_at: datetime


class AgentRunResponse(BaseModel):
    """Terminal result of one bounded run."""

    run_id: str
    session_id: str
    trigger_reason: str
    status: str
    steps: list[AgentTraceRead]


__all__ = [
    "AgentAction",
    "AgentActionName",
    "AgentRunRequest",
    "AgentRunResponse",
    "AgentTraceRead",
]
