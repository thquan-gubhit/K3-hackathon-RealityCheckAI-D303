"""Knowledge Unit generation, bounded refinement, and validation services."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from uuid import uuid4

from app.config import Settings
from app.llm.adapter import LLMClient
from app.llm.prompts import (
    build_knowledge_unit_coverage_messages,
    build_knowledge_unit_generation_messages,
    build_knowledge_unit_merge_messages,
    build_knowledge_unit_split_messages,
)
from app.models.knowledge_unit import KnowledgeUnit
from app.repositories.knowledge_unit_repository import KnowledgeUnitRepository
from app.rules.knowledge_unit_rules import (
    CoverageValidation,
    DuplicateValidation,
    KnowledgeUnitAction,
    KnowledgeUnitRuleDecision,
    compute_adjacent_signals,
    evaluate_knowledge_unit,
    validate_duplicate_units,
    validate_source_coverage,
)
from app.schemas.knowledge_unit import (
    KnowledgeUnitBatch,
    KnowledgeUnitCandidate,
    KnowledgeUnitCreate,
)


class KnowledgeUnitServiceError(RuntimeError):
    """Recoverable domain error with a stable, transport-neutral code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class SourceSegment:
    """Internal source text passed to the LLM; never used as an API response."""

    segment_id: str
    source_pages: tuple[int, ...]
    text: str
    heading: str | None = None

    def __post_init__(self) -> None:
        segment_id = self.segment_id.strip()
        text = self.text.strip()
        pages = tuple(sorted(set(self.source_pages)))
        heading = self.heading.strip() if self.heading is not None else None
        if not segment_id:
            raise ValueError("segment_id must be non-empty")
        if not pages or any(page < 1 for page in pages):
            raise ValueError("source_pages must be positive and non-empty")
        if not text:
            raise ValueError("segment text must be non-empty")
        object.__setattr__(self, "segment_id", segment_id)
        object.__setattr__(self, "source_pages", pages)
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "heading", heading or None)


@dataclass(frozen=True, slots=True)
class KnowledgeUnitBatchValidation:
    """Complete validation evidence for a candidate Knowledge Map."""

    is_valid: bool
    decisions: tuple[KnowledgeUnitRuleDecision, ...]
    coverage: CoverageValidation
    duplicates: DuplicateValidation
    errors: tuple[str, ...]


class KnowledgeUnitService:
    """Coordinate semantic LLM work while keeping acceptance deterministic."""

    def __init__(
        self,
        settings: Settings,
        *,
        llm_client: LLMClient | None = None,
        repository: KnowledgeUnitRepository | None = None,
    ) -> None:
        self._settings = settings
        self._llm_client = llm_client
        self._repository = repository

    def _llm(self) -> LLMClient:
        if self._llm_client is None:
            self._llm_client = LLMClient(self._settings)
        return self._llm_client

    def generate_candidates(
        self,
        document_id: str,
        segments: Sequence[SourceSegment],
        *,
        min_units: int = 3,
        max_units: int = 10,
    ) -> KnowledgeUnitBatch:
        """Generate an initial candidate batch without accepting or saving it."""

        messages = build_knowledge_unit_generation_messages(
            document_id,
            segments,
            min_units=min_units,
            max_units=max_units,
        )
        return self._llm().generate_structured(messages, KnowledgeUnitBatch)

    def refine_split(
        self,
        candidate: KnowledgeUnitCandidate,
        segments: Sequence[SourceSegment],
        *,
        refinement_round: int,
    ) -> KnowledgeUnitBatch:
        """Split one broad candidate and verify exact source-page preservation."""

        self._check_refinement_round(refinement_round)
        relevant_segments = _select_segments(segments, candidate.source_pages)
        messages = build_knowledge_unit_split_messages(
            candidate,
            relevant_segments,
            refinement_round=refinement_round,
        )
        batch = self._llm().generate_structured(messages, KnowledgeUnitBatch)
        if len(batch.candidates) < 2:
            raise KnowledgeUnitServiceError(
                "INVALID_SPLIT_REFINEMENT",
                "A split refinement must return at least two candidates.",
            )
        self._require_exact_page_preservation(
            batch.candidates,
            candidate.source_pages,
            error_code="INVALID_SPLIT_REFINEMENT",
        )
        return batch

    def refine_merge(
        self,
        left: KnowledgeUnitCandidate,
        right: KnowledgeUnitCandidate,
        segments: Sequence[SourceSegment],
        *,
        refinement_round: int,
    ) -> KnowledgeUnitBatch:
        """Merge adjacent fragments and verify their combined source coverage."""

        self._check_refinement_round(refinement_round)
        source_pages = sorted(set(left.source_pages) | set(right.source_pages))
        relevant_segments = _select_segments(segments, source_pages)
        messages = build_knowledge_unit_merge_messages(
            left,
            right,
            relevant_segments,
            refinement_round=refinement_round,
        )
        batch = self._llm().generate_structured(messages, KnowledgeUnitBatch)
        if len(batch.candidates) != 1:
            raise KnowledgeUnitServiceError(
                "INVALID_MERGE_REFINEMENT",
                "A merge refinement must return exactly one candidate.",
            )
        self._require_exact_page_preservation(
            batch.candidates,
            source_pages,
            error_code="INVALID_MERGE_REFINEMENT",
        )
        return batch

    def refine_coverage(
        self,
        candidates: Sequence[KnowledgeUnitCandidate],
        segments: Sequence[SourceSegment],
        *,
        expected_pages: Sequence[int],
        missing_pages: Sequence[int],
        unexpected_pages: Sequence[int],
        refinement_round: int,
    ) -> KnowledgeUnitBatch:
        """Revise the complete map to restore truthful source-page coverage."""

        self._check_refinement_round(refinement_round)
        messages = build_knowledge_unit_coverage_messages(
            candidates,
            segments,
            expected_pages=expected_pages,
            missing_pages=missing_pages,
            unexpected_pages=unexpected_pages,
            refinement_round=refinement_round,
        )
        return self._llm().generate_structured(messages, KnowledgeUnitBatch)

    def validate_candidate(
        self,
        candidate: KnowledgeUnitCandidate,
        *,
        refinement_round: int = 0,
        next_candidate: KnowledgeUnitCandidate | None = None,
    ) -> KnowledgeUnitRuleDecision:
        adjacent = (
            compute_adjacent_signals(candidate, next_candidate)
            if next_candidate is not None
            else None
        )
        return evaluate_knowledge_unit(
            candidate,
            self._settings,
            refinement_round=refinement_round,
            adjacent=adjacent,
        )

    def validate_batch(
        self,
        batch: KnowledgeUnitBatch,
        expected_pages: Sequence[int] | set[int],
        *,
        excluded_pages: Mapping[int, str] | None = None,
        refinement_round: int = 0,
        min_units: int = 3,
        max_units: int = 10,
    ) -> KnowledgeUnitBatchValidation:
        """Validate unit count, rules, references, coverage, and duplicates."""

        if min_units < 1 or max_units < min_units or max_units > 10:
            raise ValueError(
                "unit bounds must satisfy 1 <= min_units <= max_units <= 10"
            )

        decisions = tuple(
            self.validate_candidate(
                candidate,
                refinement_round=refinement_round,
                next_candidate=(
                    batch.candidates[index + 1]
                    if index + 1 < len(batch.candidates)
                    else None
                ),
            )
            for index, candidate in enumerate(batch.candidates)
        )
        coverage = validate_source_coverage(
            batch.candidates,
            expected_pages,
            excluded_pages=excluded_pages,
        )
        duplicates = validate_duplicate_units(batch.candidates)
        errors: list[str] = []

        if not min_units <= len(batch.candidates) <= max_units:
            errors.append("UNIT_COUNT_OUT_OF_RANGE")
        for index, decision in enumerate(decisions):
            if decision.action is not KnowledgeUnitAction.ACCEPT:
                errors.append(f"CANDIDATE_{index}_{decision.action.value}")
        if not coverage.is_valid:
            errors.append("SOURCE_COVERAGE_INVALID")
        if not duplicates.is_valid:
            errors.append("DUPLICATE_KNOWLEDGE_UNITS")
        errors.extend(_prerequisite_errors(batch.candidates))

        return KnowledgeUnitBatchValidation(
            is_valid=not errors,
            decisions=decisions,
            coverage=coverage,
            duplicates=duplicates,
            errors=tuple(errors),
        )

    def prepare_for_persistence(
        self,
        document_id: str,
        batch: KnowledgeUnitBatch,
        *,
        validation: KnowledgeUnitBatchValidation | None = None,
    ) -> list[KnowledgeUnitCreate]:
        """Assign stable IDs/order after the map has passed all validation gates."""

        if not document_id.strip():
            raise ValueError("document_id must be non-empty")
        if validation is None:
            represented_pages = {
                page
                for candidate in batch.candidates
                for page in candidate.source_pages
            }
            validation = self.validate_batch(batch, represented_pages)
        if not validation.is_valid:
            raise KnowledgeUnitServiceError(
                "NO_VALID_KNOWLEDGE_UNITS",
                "The Knowledge Unit batch did not pass deterministic validation.",
            )

        unit_ids = [str(uuid4()) for _candidate in batch.candidates]
        candidate_id_map = {
            candidate.candidate_id.casefold(): unit_ids[index]
            for index, candidate in enumerate(batch.candidates)
            if candidate.candidate_id is not None
        }
        units: list[KnowledgeUnitCreate] = []
        for position, candidate in enumerate(batch.candidates, start=1):
            content = candidate.model_dump(
                exclude={
                    "candidate_id",
                    "has_independent_objective",
                    "is_only_example",
                    "can_generate_independent_question",
                    "prerequisites",
                }
            )
            prerequisites = [
                candidate_id_map[prerequisite.casefold()]
                for prerequisite in candidate.prerequisites
            ]
            units.append(
                KnowledgeUnitCreate(
                    id=unit_ids[position - 1],
                    document_id=document_id,
                    position=position,
                    prerequisites=prerequisites,
                    **content,
                )
            )
        return units

    def replace_map(
        self,
        document_id: str,
        batch: KnowledgeUnitBatch,
        *,
        validation: KnowledgeUnitBatchValidation | None = None,
    ) -> list[KnowledgeUnit]:
        """Stage an all-or-nothing Knowledge Map replacement; caller commits."""

        if self._repository is None:
            raise KnowledgeUnitServiceError(
                "REPOSITORY_NOT_CONFIGURED",
                "KnowledgeUnitRepository is required to persist a Knowledge Map.",
            )
        units = self.prepare_for_persistence(
            document_id,
            batch,
            validation=validation,
        )
        return self._repository.replace_for_document(document_id, units)

    def _check_refinement_round(self, refinement_round: int) -> None:
        if refinement_round < 1:
            raise ValueError("refinement_round must be at least 1")
        if refinement_round > self._settings.ku_max_refinement_rounds:
            raise KnowledgeUnitServiceError(
                "KU_REFINEMENT_LIMIT",
                "Knowledge Unit refinement exceeded the configured round limit.",
            )

    @staticmethod
    def _require_exact_page_preservation(
        candidates: Sequence[KnowledgeUnitCandidate],
        expected_pages: Sequence[int],
        *,
        error_code: str,
    ) -> None:
        coverage = validate_source_coverage(candidates, set(expected_pages))
        if not coverage.is_valid:
            raise KnowledgeUnitServiceError(
                error_code,
                "Knowledge Unit refinement did not preserve source-page coverage.",
            )


def _select_segments(
    segments: Sequence[SourceSegment],
    source_pages: Sequence[int],
) -> list[SourceSegment]:
    expected = set(source_pages)
    selected = [
        segment
        for segment in segments
        if expected.intersection(segment.source_pages)
    ]
    represented = {
        page
        for segment in selected
        for page in segment.source_pages
        if page in expected
    }
    if represented != expected:
        raise KnowledgeUnitServiceError(
            "SOURCE_SEGMENT_MISSING",
            "Source segments do not cover every page required for refinement.",
        )
    return selected


def _prerequisite_errors(
    candidates: Sequence[KnowledgeUnitCandidate],
) -> list[str]:
    known_ids = {
        candidate.candidate_id.casefold()
        for candidate in candidates
        if candidate.candidate_id is not None
    }
    errors: list[str] = []
    for index, candidate in enumerate(candidates):
        candidate_id = (
            candidate.candidate_id.casefold()
            if candidate.candidate_id is not None
            else None
        )
        prerequisites = {
            prerequisite.casefold() for prerequisite in candidate.prerequisites
        }
        if candidate_id is not None and candidate_id in prerequisites:
            errors.append(f"CANDIDATE_{index}_SELF_PREREQUISITE")
        if prerequisites - known_ids:
            errors.append(f"CANDIDATE_{index}_UNKNOWN_PREREQUISITE")
    return errors


__all__ = [
    "KnowledgeUnitBatchValidation",
    "KnowledgeUnitService",
    "KnowledgeUnitServiceError",
    "SourceSegment",
]
