"""Deterministic Tutor Agent activation policy."""

from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings


@dataclass(frozen=True, slots=True)
class AgentTriggerInput:
    """Evidence snapshot used to accept or reject an activation request."""

    same_misconception_count: int = 0
    latest_score: float | None = None
    remediation_attempts: int = 0
    recall_score: float = 0.0
    application_score: float = 0.0
    explicit_request: bool = False


@dataclass(frozen=True, slots=True)
class AgentTriggerDecision:
    """Auditable activation result."""

    activate: bool
    reason: str
    rule_id: str


def evaluate_agent_trigger(
    evidence: AgentTriggerInput,
    settings: Settings,
) -> AgentTriggerDecision:
    """Apply the disabled gate before every other trigger."""

    if not settings.agent_enabled:
        return AgentTriggerDecision(False, "AGENT_DISABLED", "AG-001")
    if evidence.same_misconception_count >= settings.agent_trigger_wrong_count:
        return AgentTriggerDecision(
            True,
            "REPEATED_MISCONCEPTION",
            "AG-002",
        )
    if (
        evidence.latest_score is not None
        and evidence.latest_score < settings.agent_trigger_low_score
        and evidence.remediation_attempts >= 2
    ):
        return AgentTriggerDecision(
            True,
            "FAILED_REMEDIATION",
            "AG-003",
        )
    if (
        evidence.recall_score - evidence.application_score
        >= settings.agent_trigger_recall_application_gap
        and evidence.recall_score > 0
    ):
        return AgentTriggerDecision(
            True,
            "RECALL_APPLICATION_GAP",
            "AG-004",
        )
    if evidence.explicit_request:
        return AgentTriggerDecision(
            True,
            "EXPLICIT_DIFFERENT_EXPLANATION",
            "AG-EXPLICIT-001",
        )
    return AgentTriggerDecision(False, "AGENT_NOT_ELIGIBLE", "AG-NONE")


__all__ = [
    "AgentTriggerDecision",
    "AgentTriggerInput",
    "evaluate_agent_trigger",
]
