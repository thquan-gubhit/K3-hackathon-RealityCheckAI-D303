"""Deterministic validation rules for Knowledge Unit candidates and maps."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from collections.abc import Mapping, Sequence

from app.config import Settings
from app.schemas.knowledge_unit import KnowledgeUnitCandidate, KnowledgeUnitContent


class KnowledgeUnitAction(str, Enum):
    """Terminal or refinement action selected by the KU rule engine."""

    ACCEPT = "ACCEPT"
    SPLIT = "SPLIT"
    MERGE = "MERGE"
    STOP_INVALID = "STOP_INVALID"


@dataclass(frozen=True, slots=True)
class AdjacentUnitSignals:
    """Semantic signals that rules may consume but never infer via an LLM."""

    topic_similarity_is_high: bool = False
    learning_objectives_overlap_is_high: bool = False
    topic_similarity: float = 0.0
    learning_objective_overlap: float = 0.0


@dataclass(frozen=True, slots=True)
class KnowledgeUnitRuleDecision:
    """Auditable result from evaluating one candidate."""

    action: KnowledgeUnitAction
    triggered_rules: tuple[str, ...]
    reason: str
    input_summary: Mapping[str, object]


@dataclass(frozen=True, slots=True)
class CoverageValidation:
    """Coverage result for readable and explicitly excluded source pages."""

    is_valid: bool
    covered_pages: tuple[int, ...]
    excluded_pages: tuple[int, ...]
    missing_pages: tuple[int, ...]
    unexpected_pages: tuple[int, ...]
    invalid_exclusions: tuple[int, ...]
    units_without_source_pages: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class DuplicatePair:
    """One pair of materially redundant candidate positions."""

    left_index: int
    right_index: int
    reason: str
    concept_similarity: float
    objective_similarity: float


@dataclass(frozen=True, slots=True)
class DuplicateValidation:
    """Serious duplicate check over a complete candidate batch."""

    is_valid: bool
    pairs: tuple[DuplicatePair, ...]


def _validate_settings(settings: Settings) -> None:
    if settings.ku_min_concepts > settings.ku_max_concepts:
        raise ValueError("KU_MIN_CONCEPTS cannot exceed KU_MAX_CONCEPTS")
    if settings.ku_min_reading_minutes > settings.ku_max_reading_minutes:
        raise ValueError(
            "KU_MIN_READING_MINUTES cannot exceed KU_MAX_READING_MINUTES"
        )


def evaluate_knowledge_unit(
    candidate: KnowledgeUnitCandidate,
    settings: Settings,
    *,
    refinement_round: int = 0,
    adjacent: AdjacentUnitSignals | None = None,
) -> KnowledgeUnitRuleDecision:
    """Evaluate one candidate using the documented split/merge priorities.

    Split has priority over merge because a broad candidate must not absorb
    more content. The refinement limit only converts a candidate to
    ``STOP_INVALID`` when it still needs a split or merge; a valid candidate at
    the boundary remains acceptable.
    """

    _validate_settings(settings)
    if refinement_round < 0:
        raise ValueError("refinement_round must be non-negative")

    adjacent = adjacent or AdjacentUnitSignals()
    summary: dict[str, object] = {
        "learning_objective_count": len(candidate.learning_objectives),
        "key_concept_count": len(candidate.key_concepts),
        "estimated_reading_minutes": candidate.estimated_reading_minutes,
        "has_independent_objective": candidate.has_independent_objective,
        "is_only_example": candidate.is_only_example,
        "can_generate_independent_question": (
            candidate.can_generate_independent_question
        ),
        "topic_similarity_with_next_is_high": (
            adjacent.topic_similarity_is_high
        ),
        "learning_objectives_overlap_with_next_is_high": (
            adjacent.learning_objectives_overlap_is_high
        ),
        "refinement_round": refinement_round,
    }

    if not candidate.key_concepts:
        return KnowledgeUnitRuleDecision(
            action=KnowledgeUnitAction.STOP_INVALID,
            triggered_rules=("KU-INVALID-001",),
            reason="The candidate has no key concept and cannot form a Knowledge Unit.",
            input_summary=summary,
        )

    split_rules: list[tuple[str, str]] = []
    merge_rules: list[tuple[str, str]] = []

    if len(candidate.learning_objectives) > settings.ku_max_learning_objectives:
        split_rules.append(
            (
                "KU-SPLIT-001",
                "learning objectives exceed KU_MAX_LEARNING_OBJECTIVES",
            )
        )
    if len(candidate.key_concepts) > settings.ku_max_concepts:
        split_rules.append(
            ("KU-SPLIT-002", "key concepts exceed KU_MAX_CONCEPTS")
        )
    if candidate.estimated_reading_minutes > settings.ku_max_reading_minutes:
        split_rules.append(
            (
                "KU-SPLIT-003",
                "estimated reading time exceeds KU_MAX_READING_MINUTES",
            )
        )

    if (
        len(candidate.key_concepts) < settings.ku_min_concepts
        and not candidate.has_independent_objective
    ):
        merge_rules.append(
            (
                "KU-MERGE-001",
                "the fragment has too few concepts and no independent objective",
            )
        )
    if (
        candidate.estimated_reading_minutes
        < settings.ku_min_reading_minutes
        and candidate.is_only_example
    ):
        merge_rules.append(
            (
                "KU-MERGE-002",
                "the short fragment is only an example",
            )
        )
    if not candidate.can_generate_independent_question:
        merge_rules.append(
            (
                "KU-MERGE-003",
                "the candidate is not independently assessable",
            )
        )
    if (
        adjacent.topic_similarity_is_high
        and adjacent.learning_objectives_overlap_is_high
    ):
        merge_rules.append(
            (
                "KU-MERGE-004",
                "the adjacent unit is highly similar with overlapping objectives",
            )
        )

    triggered = split_rules if split_rules else merge_rules
    if not triggered:
        return KnowledgeUnitRuleDecision(
            action=KnowledgeUnitAction.ACCEPT,
            triggered_rules=(),
            reason="The candidate satisfies all configured Knowledge Unit rules.",
            input_summary=summary,
        )

    action = (
        KnowledgeUnitAction.SPLIT
        if split_rules
        else KnowledgeUnitAction.MERGE
    )
    rule_ids = tuple(rule_id for rule_id, _ in triggered)
    reasons = "; ".join(reason for _, reason in triggered)

    if refinement_round >= settings.ku_max_refinement_rounds:
        return KnowledgeUnitRuleDecision(
            action=KnowledgeUnitAction.STOP_INVALID,
            triggered_rules=rule_ids + ("KU-LIMIT-001",),
            reason=(
                f"{reasons}; refinement reached KU_MAX_REFINEMENT_ROUNDS"
            ),
            input_summary=summary,
        )

    return KnowledgeUnitRuleDecision(
        action=action,
        triggered_rules=rule_ids,
        reason=reasons,
        input_summary=summary,
    )


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _normalized_labels(values: Sequence[str]) -> set[str]:
    return {" ".join(value.casefold().split()) for value in values if value.strip()}


def _word_set(values: Sequence[str]) -> set[str]:
    return {
        token
        for value in values
        for token in re.findall(r"\w+", value.casefold(), flags=re.UNICODE)
        if len(token) > 1
    }


def compute_adjacent_signals(
    current: KnowledgeUnitContent,
    next_unit: KnowledgeUnitContent,
    *,
    high_similarity_threshold: float = 0.75,
) -> AdjacentUnitSignals:
    """Compute reproducible adjacent-unit measurements from candidate metadata."""

    if not 0.0 <= high_similarity_threshold <= 1.0:
        raise ValueError("high_similarity_threshold must be between 0 and 1")

    concept_similarity = _jaccard(
        _normalized_labels(current.key_concepts),
        _normalized_labels(next_unit.key_concepts),
    )
    title_similarity = _jaccard(
        _word_set([current.title]),
        _word_set([next_unit.title]),
    )
    topic_similarity = max(concept_similarity, title_similarity)
    objective_similarity = _jaccard(
        _word_set(current.learning_objectives),
        _word_set(next_unit.learning_objectives),
    )
    return AdjacentUnitSignals(
        topic_similarity_is_high=topic_similarity >= high_similarity_threshold,
        learning_objectives_overlap_is_high=(
            objective_similarity >= high_similarity_threshold
        ),
        topic_similarity=topic_similarity,
        learning_objective_overlap=objective_similarity,
    )


def validate_source_coverage(
    units: Sequence[KnowledgeUnitContent],
    expected_pages: Sequence[int] | set[int],
    *,
    excluded_pages: Mapping[int, str] | None = None,
) -> CoverageValidation:
    """Require every readable page to be covered or excluded with a reason."""

    expected = set(expected_pages)
    if any(page < 1 for page in expected):
        raise ValueError("expected_pages must contain only positive integers")

    covered: set[int] = set()
    units_without_pages: list[int] = []
    for index, unit in enumerate(units):
        if not unit.source_pages:
            units_without_pages.append(index)
        covered.update(unit.source_pages)

    exclusions = excluded_pages or {}
    valid_exclusions = {
        page
        for page, reason in exclusions.items()
        if page in expected and page > 0 and bool(reason.strip())
    }
    invalid_exclusions = {
        page
        for page, reason in exclusions.items()
        if page not in expected or page < 1 or not reason.strip()
    }
    missing = expected - covered - valid_exclusions
    unexpected = covered - expected

    is_valid = not (
        missing
        or unexpected
        or invalid_exclusions
        or units_without_pages
    )
    return CoverageValidation(
        is_valid=is_valid,
        covered_pages=tuple(sorted(covered & expected)),
        excluded_pages=tuple(sorted(valid_exclusions)),
        missing_pages=tuple(sorted(missing)),
        unexpected_pages=tuple(sorted(unexpected)),
        invalid_exclusions=tuple(sorted(invalid_exclusions)),
        units_without_source_pages=tuple(units_without_pages),
    )


def validate_duplicate_units(
    units: Sequence[KnowledgeUnitContent],
    *,
    similarity_threshold: float = 0.80,
) -> DuplicateValidation:
    """Reject exact-title or strongly overlapping concept/objective duplicates."""

    if not 0.0 <= similarity_threshold <= 1.0:
        raise ValueError("similarity_threshold must be between 0 and 1")

    pairs: list[DuplicatePair] = []
    for left_index, left in enumerate(units):
        for right_index in range(left_index + 1, len(units)):
            right = units[right_index]
            titles_match = (
                " ".join(left.title.casefold().split())
                == " ".join(right.title.casefold().split())
            )
            concept_similarity = _jaccard(
                _normalized_labels(left.key_concepts),
                _normalized_labels(right.key_concepts),
            )
            objective_similarity = _jaccard(
                _word_set(left.learning_objectives),
                _word_set(right.learning_objectives),
            )
            metadata_matches = (
                concept_similarity >= similarity_threshold
                and objective_similarity >= similarity_threshold
            )
            if titles_match or metadata_matches:
                reason = (
                    "normalized titles are identical"
                    if titles_match
                    else "concept and objective overlap exceeds the threshold"
                )
                pairs.append(
                    DuplicatePair(
                        left_index=left_index,
                        right_index=right_index,
                        reason=reason,
                        concept_similarity=concept_similarity,
                        objective_similarity=objective_similarity,
                    )
                )

    return DuplicateValidation(is_valid=not pairs, pairs=tuple(pairs))


__all__ = [
    "AdjacentUnitSignals",
    "CoverageValidation",
    "DuplicatePair",
    "DuplicateValidation",
    "KnowledgeUnitAction",
    "KnowledgeUnitRuleDecision",
    "compute_adjacent_signals",
    "evaluate_knowledge_unit",
    "validate_duplicate_units",
    "validate_source_coverage",
]
