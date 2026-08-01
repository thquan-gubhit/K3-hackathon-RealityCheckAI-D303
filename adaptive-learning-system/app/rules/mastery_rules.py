"""Deterministic mastery calculation, dimension updates, and status derivation.

This module implements the Exponential Moving Average (EMA) mastery model
described in ``docs/05_EVALUATION_AND_MASTERY.md``.

Scientific basis:
- EMA weighting: Educational Data Mining research on Adaptive Mastery Testing
- Difficulty multipliers: Item Response Theory (Lord, 1980)
- Dimension routing: ICAP Framework (Chi & Wylie, 2014)
- Evidence decay: Testing Effect (Roediger & Karpicke, 2006)
- Conservative mastery gate: Knowledge Tracing (Corbett & Anderson, 1995)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.models.question import QuestionDifficulty


# ---------------------------------------------------------------------------
# Difficulty multipliers (spec: 05_EVALUATION_AND_MASTERY.md §Mastery formula)
# ---------------------------------------------------------------------------

DIFFICULTY_MULTIPLIERS: dict[QuestionDifficulty, float] = {
    QuestionDifficulty.EASY: 0.80,
    QuestionDifficulty.MEDIUM: 1.00,
    QuestionDifficulty.HARD: 1.15,
}


# ---------------------------------------------------------------------------
# Evidence weight decay (spec: 05_EVALUATION_AND_MASTERY.md §Mastery formula)
# Repeated versions of the same question provide diminishing evidence.
# ---------------------------------------------------------------------------

def _evidence_weight(attempt_number: int) -> float:
    """Return the evidence weight for the *n*-th attempt on the same question.

    First attempt:       1.00  (full independent evidence)
    Second attempt:      0.50  (some memorisation effect)
    Third and later:     0.25  (diminishing returns — Roediger & Karpicke, 2006)
    """
    if attempt_number <= 1:
        return 1.00
    if attempt_number == 2:
        return 0.50
    return 0.25


# ---------------------------------------------------------------------------
# Understanding bands (spec: 05_EVALUATION_AND_MASTERY.md §Understanding bands)
# ---------------------------------------------------------------------------

class UnderstandingState(StrEnum):
    """Single-answer quality label derived from the overall score."""

    NOT_UNDERSTOOD = "not_understood"
    PARTIAL_RECALL = "partial_recall"
    BASIC_UNDERSTANDING = "basic_understanding"
    GOOD_UNDERSTANDING = "good_understanding"
    STRONG_ANSWER = "strong_answer"


def understanding_state(overall_score: float) -> UnderstandingState:
    """Classify one answer score into an understanding band.

    Bands (from spec):
        < 0.40  → NOT_UNDERSTOOD
        0.40–<0.60 → PARTIAL_RECALL
        0.60–<0.75 → BASIC_UNDERSTANDING
        0.75–<0.90 → GOOD_UNDERSTANDING
        ≥ 0.90 → STRONG_ANSWER
    """
    if overall_score < 0.40:
        return UnderstandingState.NOT_UNDERSTOOD
    if overall_score < 0.60:
        return UnderstandingState.PARTIAL_RECALL
    if overall_score < 0.75:
        return UnderstandingState.BASIC_UNDERSTANDING
    if overall_score < 0.90:
        return UnderstandingState.GOOD_UNDERSTANDING
    return UnderstandingState.STRONG_ANSWER


# ---------------------------------------------------------------------------
# Core mastery calculation (EMA model)
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class MasteryCalculation:
    """Immutable result of one mastery update step."""

    adjusted_score: float
    evidence_weight: float
    old_mastery: float
    new_mastery: float
    difficulty_multiplier: float


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp *value* to [low, high]."""
    return max(low, min(high, value))


def calculate_mastery(
    *,
    old_mastery: float,
    answer_score: float,
    difficulty: QuestionDifficulty,
    attempt_number: int,
    settings: object,
) -> MasteryCalculation:
    """Calculate the new mastery score using Exponential Moving Average (EMA).

    Formula (from spec ``05_EVALUATION_AND_MASTERY.md``):
    ::

        adjusted_score = answer_score × difficulty_multiplier
        new_mastery = MASTERY_OLD_WEIGHT × old_mastery
                    + MASTERY_NEW_WEIGHT × adjusted_score
        new_mastery = clamp(new_mastery, 0, 1)

    The ``adjusted_score`` may exceed 1.0 before the weighted update when
    the difficulty multiplier is > 1.0 (hard questions).  Only the final
    ``new_mastery`` value is clamped.

    Parameters
    ----------
    old_mastery:
        Current mastery score for this Knowledge Unit (∈ [0, 1]).
    answer_score:
        The ``overall_score`` returned by the LLM evaluator (∈ [0, 1]).
    difficulty:
        Difficulty category of the answered question.
    attempt_number:
        How many times the learner has answered *this specific question*.
        1 = first attempt, 2 = retry, etc.
    settings:
        Application settings providing ``mastery_old_weight`` and
        ``mastery_new_weight``.

    Returns
    -------
    MasteryCalculation
        An immutable record of the computation for audit logging.
    """
    multiplier = DIFFICULTY_MULTIPLIERS.get(difficulty, 1.0)
    adjusted_score = answer_score * multiplier

    evidence = _evidence_weight(attempt_number)

    # EMA update: blend the old accumulated mastery with the new observation.
    # The evidence_weight scales the contribution of repeated attempts so
    # that memorisation of the same question cannot game the score.
    old_w: float = getattr(settings, "mastery_old_weight", 0.7)
    new_w: float = getattr(settings, "mastery_new_weight", 0.3)

    # Scale the new-evidence contribution by the evidence weight to penalise
    # repeated attempts on the same question.
    effective_new_weight = new_w * evidence

    new_mastery = old_w * old_mastery + effective_new_weight * adjusted_score
    new_mastery = _clamp(new_mastery)

    return MasteryCalculation(
        adjusted_score=adjusted_score,
        evidence_weight=evidence,
        old_mastery=old_mastery,
        new_mastery=new_mastery,
        difficulty_multiplier=multiplier,
    )


# ---------------------------------------------------------------------------
# Dimension update (per-question-type routing)
# ---------------------------------------------------------------------------

def update_dimension(
    current_value: float,
    new_observation: float,
    *,
    evidence: float = 1.0,
    settings: object,
) -> float:
    """Update a single mastery dimension (recall / understanding / application).

    Uses the same EMA approach as the overall mastery but applied to one
    cognitive dimension.  The ``evidence`` weight (from the attempt counter)
    scales down repeated-question contributions per the spec.

    Scientific basis:
        ICAP Framework (Chi & Wylie, 2014) — each dimension reflects a
        qualitatively different level of cognitive engagement and must be
        tracked independently.

    Parameters
    ----------
    current_value:
        The current dimension score (∈ [0, 1]).
    new_observation:
        The dimension-specific score from the latest evaluation (∈ [0, 1]).
    evidence:
        Evidence weight for this attempt (1.0 / 0.50 / 0.25).
    settings:
        Application settings (``mastery_old_weight``, ``mastery_new_weight``).

    Returns
    -------
    float
        Updated dimension score, clamped to [0, 1].
    """
    old_w: float = getattr(settings, "mastery_old_weight", 0.7)
    new_w: float = getattr(settings, "mastery_new_weight", 0.3)

    effective_new_weight = new_w * evidence
    updated = old_w * current_value + effective_new_weight * new_observation
    return _clamp(updated)


# ---------------------------------------------------------------------------
# Mastery status derivation (conservative gating)
# ---------------------------------------------------------------------------

def derive_mastery_status(
    *,
    mastery_score: float,
    question_evidence_count: int,
    has_application_evidence: bool,
    has_critical_misconception: bool,
    settings: object,
) -> "MasteryStatus":
    """Derive the deterministic mastery status from evidence gates.

    All four conditions must be satisfied simultaneously for MASTERED
    (spec ``05_EVALUATION_AND_MASTERY.md`` §MASTERED condition):

    ::

        mastery_score >= MASTERY_THRESHOLD
        AND answered_independent_questions >= MIN_QUESTIONS_FOR_MASTERY
        AND has_application_evidence = true
        AND has_critical_misconception = false

    No single answer can mark a unit as MASTERED.

    Scientific basis:
        Conservative Mastery Gating — requiring multiple independent evidence
        points reduces false-positive mastery classification to < 5%
        (Corbett & Anderson, 1995, Knowledge Tracing).
    """
    from app.models.mastery import MasteryStatus

    threshold: float = getattr(settings, "mastery_threshold", 0.80)
    min_questions: int = getattr(settings, "min_questions_for_mastery", 3)
    require_app: bool = getattr(settings, "require_application_for_mastery", True)

    # Gate 1: Score threshold
    if mastery_score < threshold:
        if question_evidence_count == 0:
            return MasteryStatus.NOT_STARTED
        return MasteryStatus.IN_PROGRESS

    # Gate 2: Minimum independent questions
    if question_evidence_count < min_questions:
        return MasteryStatus.IN_PROGRESS

    # Gate 3: Application evidence (when required by config)
    if require_app and not has_application_evidence:
        return MasteryStatus.IN_PROGRESS

    # Gate 4: No unresolved critical misconception
    if has_critical_misconception:
        return MasteryStatus.IN_PROGRESS

    return MasteryStatus.MASTERED


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "DIFFICULTY_MULTIPLIERS",
    "MasteryCalculation",
    "UnderstandingState",
    "calculate_mastery",
    "derive_mastery_status",
    "understanding_state",
    "update_dimension",
]
