"""Deterministic Tutor Agent trigger and disabled-gate tests."""

from __future__ import annotations

from app.config import Settings
from app.rules.agent_trigger_rules import (
    AgentTriggerInput,
    evaluate_agent_trigger,
)


def _settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "_env_file": None,
        "agent_enabled": True,
        "agent_trigger_wrong_count": 2,
        "agent_trigger_low_score": 0.4,
        "agent_trigger_recall_application_gap": 0.25,
    }
    values.update(overrides)
    return Settings(**values)  # type: ignore[arg-type]


def test_disabled_agent_never_activates_even_on_strong_trigger() -> None:
    decision = evaluate_agent_trigger(
        AgentTriggerInput(
            same_misconception_count=99,
            explicit_request=True,
        ),
        _settings(agent_enabled=False),
    )

    assert decision.activate is False
    assert decision.reason == "AGENT_DISABLED"


def test_repeated_misconception_activates_agent() -> None:
    decision = evaluate_agent_trigger(
        AgentTriggerInput(same_misconception_count=2),
        _settings(),
    )

    assert decision.activate is True
    assert decision.reason == "REPEATED_MISCONCEPTION"


def test_low_score_requires_two_remediation_attempts() -> None:
    not_yet = evaluate_agent_trigger(
        AgentTriggerInput(latest_score=0.2, remediation_attempts=1),
        _settings(),
    )
    active = evaluate_agent_trigger(
        AgentTriggerInput(latest_score=0.2, remediation_attempts=2),
        _settings(),
    )

    assert not_yet.activate is False
    assert active.reason == "FAILED_REMEDIATION"


def test_recall_application_gap_is_configured() -> None:
    decision = evaluate_agent_trigger(
        AgentTriggerInput(recall_score=0.8, application_score=0.5),
        _settings(),
    )

    assert decision.activate is True
    assert decision.reason == "RECALL_APPLICATION_GAP"


def test_explicit_request_activates_without_other_evidence() -> None:
    decision = evaluate_agent_trigger(
        AgentTriggerInput(explicit_request=True),
        _settings(),
    )

    assert decision.activate is True
    assert decision.reason == "EXPLICIT_DIFFERENT_EXPLANATION"
