"""Exact threshold and evidence tests for Phase 4 rules."""

from __future__ import annotations

import pytest

from app.config import Settings
from app.models.mastery import MasteryStatus
from app.models.question import QuestionDifficulty, QuestionType
from app.rules.mastery_rules import (
    UnderstandingState,
    calculate_mastery,
    derive_mastery_status,
    evidence_weight,
    understanding_state,
)
from app.rules.question_rules import LearningEvidence, select_next_question


def _settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "_env_file": None,
        "max_main_questions_per_unit": 3,
        "agent_trigger_wrong_count": 2,
        "mastery_old_weight": 0.7,
        "mastery_new_weight": 0.3,
        "mastery_threshold": 0.8,
        "min_questions_for_mastery": 3,
        "require_application_for_mastery": True,
    }
    values.update(overrides)
    return Settings(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0.0, UnderstandingState.NOT_UNDERSTOOD),
        (0.3999, UnderstandingState.NOT_UNDERSTOOD),
        (0.4, UnderstandingState.PARTIAL_RECALL),
        (0.6, UnderstandingState.BASIC_UNDERSTANDING),
        (0.75, UnderstandingState.GOOD_UNDERSTANDING),
        (0.9, UnderstandingState.STRONG_ANSWER),
        (1.0, UnderstandingState.STRONG_ANSWER),
    ],
)
def test_understanding_state_boundaries(
    score: float,
    expected: UnderstandingState,
) -> None:
    assert understanding_state(score) is expected


def test_mastery_formula_and_hard_clamp() -> None:
    result = calculate_mastery(
        old_mastery=0.9,
        answer_score=1.0,
        difficulty=QuestionDifficulty.HARD,
        attempt_number=1,
        settings=_settings(),
    )

    assert result.adjusted_score == pytest.approx(1.15)
    assert result.new_mastery == pytest.approx(0.975)


def test_repeated_evidence_weights_are_bounded() -> None:
    assert evidence_weight(1) == 1.0
    assert evidence_weight(2) == 0.5
    assert evidence_weight(3) == 0.25
    assert evidence_weight(99) == 0.25


def test_mastered_requires_every_predicate() -> None:
    settings = _settings()
    assert (
        derive_mastery_status(
            mastery_score=0.8,
            question_evidence_count=3,
            has_application_evidence=True,
            has_critical_misconception=False,
            settings=settings,
        )
        is MasteryStatus.MASTERED
    )
    assert (
        derive_mastery_status(
            mastery_score=0.99,
            question_evidence_count=1,
            has_application_evidence=True,
            has_critical_misconception=False,
            settings=settings,
        )
        is MasteryStatus.IN_PROGRESS
    )
    assert (
        derive_mastery_status(
            mastery_score=0.99,
            question_evidence_count=3,
            has_application_evidence=False,
            has_critical_misconception=False,
            settings=settings,
        )
        is MasteryStatus.IN_PROGRESS
    )
    assert (
        derive_mastery_status(
            mastery_score=0.99,
            question_evidence_count=3,
            has_application_evidence=True,
            has_critical_misconception=True,
            settings=settings,
        )
        is MasteryStatus.IN_PROGRESS
    )


def test_first_question_is_recall() -> None:
    route = select_next_question(LearningEvidence(), _settings())

    assert route.question_type is QuestionType.RECALL
    assert route.rule_id == "QS-001"


def test_low_recall_gets_scaffolded_recall_route() -> None:
    route = select_next_question(
        LearningEvidence(
            answered_questions=1,
            latest_score=0.3,
            latest_recall_score=0.3,
        ),
        _settings(),
    )

    assert route.question_type is QuestionType.RECALL
    assert route.rule_id == "QS-002"


def test_mid_score_gets_explain_and_high_score_gets_apply() -> None:
    explain = select_next_question(
        LearningEvidence(answered_questions=1, latest_score=0.6),
        _settings(),
    )
    apply = select_next_question(
        LearningEvidence(answered_questions=2, latest_score=0.8),
        _settings(),
    )

    assert explain.question_type is QuestionType.EXPLAIN
    assert apply.question_type is QuestionType.APPLY


def test_recall_application_gap_has_priority() -> None:
    route = select_next_question(
        LearningEvidence(
            answered_questions=2,
            latest_score=0.8,
            recall_score=0.8,
            application_score=0.3,
        ),
        _settings(),
    )

    assert route.question_type is QuestionType.APPLY
    assert route.rule_id == "QS-005"


def test_question_cap_is_terminal_before_agent_trigger() -> None:
    route = select_next_question(
        LearningEvidence(
            answered_questions=3,
            main_question_count=3,
            same_misconception_count=3,
        ),
        _settings(),
    )

    assert route.next_action == "FINISH_OR_REMEDIATE"
    assert route.rule_id == "QS-007"
