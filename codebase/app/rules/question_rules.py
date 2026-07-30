"""Deterministic question validation and adaptive selection rules."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
from collections.abc import Sequence

from app.config import Settings
from app.models.question import QuestionType
from app.schemas.knowledge_unit import KnowledgeUnitContent
from app.schemas.question import QuestionCandidate


@dataclass(frozen=True, slots=True)
class QuestionValidationDecision:
    """Auditable acceptance decision for one generated candidate."""

    accepted: bool
    reasons: tuple[str, ...]
    content_fingerprint: str


@dataclass(frozen=True, slots=True)
class LearningEvidence:
    """Minimal history snapshot consumed by next-question rules."""

    answered_questions: int = 0
    main_question_count: int = 0
    remediation_question_count: int = 0
    latest_score: float | None = None
    latest_recall_score: float | None = None
    recall_score: float = 0.0
    application_score: float = 0.0
    same_misconception_count: int = 0


@dataclass(frozen=True, slots=True)
class QuestionRoute:
    """Winning deterministic action and desired question type."""

    next_action: str
    question_type: QuestionType | None
    rule_id: str
    reason: str


def normalize_question_text(text: str) -> str:
    """Normalize learner-visible question text for stable duplication checks."""

    return " ".join(
        re.findall(r"\w+", text.casefold(), flags=re.UNICODE)
    )


def question_fingerprint(text: str) -> str:
    """Return a stable content fingerprint without storing source context."""

    return sha256(normalize_question_text(text).encode("utf-8")).hexdigest()


def _word_set(text: str) -> set[str]:
    return {
        token
        for token in normalize_question_text(text).split()
        if len(token) > 1
    }


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def validate_question_candidate(
    candidate: QuestionCandidate,
    unit: KnowledgeUnitContent,
    *,
    existing_question_texts: Sequence[str] = (),
    duplicate_threshold: float = 0.80,
) -> QuestionValidationDecision:
    """Apply all source, objective, leakage, clarity, and duplicate gates."""

    if not 0.0 <= duplicate_threshold <= 1.0:
        raise ValueError("duplicate_threshold must be between 0 and 1")

    reasons: list[str] = []
    unit_pages = set(unit.source_pages)
    if not candidate.source_grounded or not set(candidate.source_pages) <= unit_pages:
        reasons.append("NOT_SOURCE_GROUNDED")
    objectives = {
        " ".join(objective.casefold().split())
        for objective in unit.learning_objectives
    }
    if (
        not candidate.objective_aligned
        or " ".join(candidate.learning_objective.casefold().split())
        not in objectives
    ):
        reasons.append("OBJECTIVE_MISMATCH")
    if candidate.answer_leak:
        reasons.append("ANSWER_LEAK")
    if candidate.ambiguous:
        reasons.append("AMBIGUOUS")
    if candidate.requires_external_knowledge:
        reasons.append("EXTERNAL_KNOWLEDGE_REQUIRED")

    words = _word_set(candidate.question_text)
    if any(
        _jaccard(words, _word_set(existing)) >= duplicate_threshold
        for existing in existing_question_texts
    ):
        reasons.append("DUPLICATE")

    return QuestionValidationDecision(
        accepted=not reasons,
        reasons=tuple(reasons),
        content_fingerprint=question_fingerprint(candidate.question_text),
    )


def select_next_question(
    evidence: LearningEvidence,
    settings: Settings,
) -> QuestionRoute:
    """Select a normal question or terminal/remediation action by priority."""

    if evidence.main_question_count >= settings.max_main_questions_per_unit:
        return QuestionRoute(
            next_action="FINISH_OR_REMEDIATE",
            question_type=None,
            rule_id="QS-007",
            reason="The main-question cap has been reached.",
        )
    if evidence.same_misconception_count >= settings.agent_trigger_wrong_count:
        return QuestionRoute(
            next_action="ACTIVATE_TUTOR_AGENT",
            question_type=None,
            rule_id="QS-006",
            reason="The same misconception has recurred.",
        )
    if (
        evidence.recall_score >= 0.75
        and evidence.application_score < 0.60
    ):
        return QuestionRoute(
            next_action="ASK_QUESTION",
            question_type=QuestionType.APPLY,
            rule_id="QS-005",
            reason="Application evidence lags behind recall.",
        )
    if evidence.answered_questions == 0:
        return QuestionRoute(
            next_action="ASK_QUESTION",
            question_type=QuestionType.RECALL,
            rule_id="QS-001",
            reason="No answer history exists for this unit.",
        )
    if (
        evidence.latest_recall_score is not None
        and evidence.latest_recall_score < 0.40
    ):
        return QuestionRoute(
            next_action="ASK_QUESTION",
            question_type=QuestionType.RECALL,
            rule_id="QS-002",
            reason="Recall remains below the scaffold threshold.",
        )
    if evidence.latest_score is not None and evidence.latest_score < 0.70:
        return QuestionRoute(
            next_action="ASK_QUESTION",
            question_type=QuestionType.EXPLAIN,
            rule_id="QS-003",
            reason="The latest score calls for conceptual explanation.",
        )
    return QuestionRoute(
        next_action="ASK_QUESTION",
        question_type=QuestionType.APPLY,
        rule_id="QS-004",
        reason="The learner is ready for application evidence.",
    )


__all__ = [
    "LearningEvidence",
    "QuestionRoute",
    "QuestionValidationDecision",
    "normalize_question_text",
    "question_fingerprint",
    "select_next_question",
    "validate_question_candidate",
]
