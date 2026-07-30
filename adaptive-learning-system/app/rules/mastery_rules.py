"""Pure understanding-band, evidence-weight, and mastery calculations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.config import Settings
from app.models.mastery import MasteryStatus
from app.models.question import QuestionDifficulty


class UnderstandingState(StrEnum):
    """Latest-answer state; deliberately separate from mastery."""

    NOT_UNDERSTOOD = "not_understood"
    PARTIAL_RECALL = "partial_recall"
    BASIC_UNDERSTANDING = "basic_understanding"
    GOOD_UNDERSTANDING = "good_understanding"
    STRONG_ANSWER = "strong_answer"


DIFFICULTY_MULTIPLIERS = {
    QuestionDifficulty.EASY: 0.80,
    QuestionDifficulty.MEDIUM: 1.00,
    QuestionDifficulty.HARD: 1.15,
}


@dataclass(frozen=True, slots=True)
class MasteryCalculation:
    """Evidence-weighted result with auditable intermediate values."""

    adjusted_score: float
    evidence_weight: float
    new_mastery: float


def clamp_score(value: float) -> float:
    return min(1.0, max(0.0, value))


def understanding_state(score: float) -> UnderstandingState:
    """Map an answer score to exact documented threshold bands."""

    if not 0.0 <= score <= 1.0:
        raise ValueError("score must be between 0 and 1")
    if score < 0.40:
        return UnderstandingState.NOT_UNDERSTOOD
    if score < 0.60:
        return UnderstandingState.PARTIAL_RECALL
    if score < 0.75:
        return UnderstandingState.BASIC_UNDERSTANDING
    if score < 0.90:
        return UnderstandingState.GOOD_UNDERSTANDING
    return UnderstandingState.STRONG_ANSWER


def evidence_weight(attempt_number: int) -> float:
    """Return diminishing evidence for repeated equivalent questions."""

    if attempt_number < 1:
        raise ValueError("attempt_number must be positive")
    if attempt_number == 1:
        return 1.0
    if attempt_number == 2:
        return 0.5
    return 0.25


def calculate_mastery(
    *,
    old_mastery: float,
    answer_score: float,
    difficulty: QuestionDifficulty,
    attempt_number: int,
    settings: Settings,
) -> MasteryCalculation:
    """Apply the documented formula with reduced repeated evidence."""

    if not 0.0 <= old_mastery <= 1.0:
        raise ValueError("old_mastery must be between 0 and 1")
    if not 0.0 <= answer_score <= 1.0:
        raise ValueError("answer_score must be between 0 and 1")
    if abs(settings.mastery_old_weight + settings.mastery_new_weight - 1.0) > 1e-6:
        raise ValueError("mastery weights must sum to 1.0")

    weight = evidence_weight(attempt_number)
    adjusted = answer_score * DIFFICULTY_MULTIPLIERS[difficulty]
    repeated_target = old_mastery * (1.0 - weight) + adjusted * weight
    updated = (
        settings.mastery_old_weight * old_mastery
        + settings.mastery_new_weight * repeated_target
    )
    return MasteryCalculation(
        adjusted_score=adjusted,
        evidence_weight=weight,
        new_mastery=clamp_score(updated),
    )


def update_dimension(
    old_score: float,
    new_score: float,
    *,
    evidence: float,
    settings: Settings,
) -> float:
    """Blend one dimension with the same reduced-evidence policy."""

    target = old_score * (1.0 - evidence) + new_score * evidence
    return clamp_score(
        settings.mastery_old_weight * old_score
        + settings.mastery_new_weight * target
    )


def derive_mastery_status(
    *,
    mastery_score: float,
    question_evidence_count: int,
    has_application_evidence: bool,
    has_critical_misconception: bool,
    settings: Settings,
) -> MasteryStatus:
    """Require every mastery predicate; never master from one answer."""

    if (
        mastery_score >= settings.mastery_threshold
        and question_evidence_count >= settings.min_questions_for_mastery
        and (
            has_application_evidence
            or not settings.require_application_for_mastery
        )
        and not has_critical_misconception
    ):
        return MasteryStatus.MASTERED
    return (
        MasteryStatus.IN_PROGRESS
        if question_evidence_count > 0
        else MasteryStatus.NOT_STARTED
    )


__all__ = [
    "DIFFICULTY_MULTIPLIERS",
    "MasteryCalculation",
    "UnderstandingState",
    "calculate_mastery",
    "clamp_score",
    "derive_mastery_status",
    "evidence_weight",
    "understanding_state",
    "update_dimension",
]
