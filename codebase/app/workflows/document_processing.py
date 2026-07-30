"""Deterministic document-processing workflow for the Phase 2 Knowledge Map."""

from __future__ import annotations

from dataclasses import dataclass
import logging
import re
from typing import Any, Sequence

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import Settings
from app.errors import AppError
from app.llm import (
    InvalidLLMOutputError,
    LLMProviderError,
    LLMTimeoutError,
)
from app.models.document import Document, DocumentStatus
from app.models.knowledge_unit import KnowledgeUnit
from app.repositories.document_repository import DocumentRepository
from app.repositories.knowledge_unit_repository import KnowledgeUnitRepository
from app.rules.knowledge_unit_rules import KnowledgeUnitAction
from app.schemas.knowledge_unit import (
    KnowledgeUnitBatch,
    KnowledgeUnitCandidate,
)
from app.services.document_segmentation import (
    SegmentationResult,
    create_candidate_segments,
)
from app.services.knowledge_unit_service import (
    KnowledgeUnitBatchValidation,
    KnowledgeUnitService,
    KnowledgeUnitServiceError,
    SourceSegment,
)
from app.services.pdf_parser import PdfParseError, PdfParser


logger = logging.getLogger(__name__)
_COVERAGE_TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)
_CONTINUATION_MARKERS = (
    "ví dụ",
    "thí dụ",
    "bài tập",
    "đề thi",
    "example",
    "exercise",
)
_COVERAGE_STOP_WORDS = {
    "và",
    "của",
    "cho",
    "một",
    "các",
    "là",
    "the",
    "and",
    "for",
    "with",
}


@dataclass(frozen=True, slots=True)
class ProcessingCoverage:
    """Compact coverage evidence returned to API clients."""

    readable_pages: int
    covered_pages: int
    coverage_ratio: float


@dataclass(frozen=True, slots=True)
class DocumentProcessingResult:
    """Successful persisted output of the document workflow."""

    document: Document
    knowledge_units: tuple[KnowledgeUnit, ...]
    coverage: ProcessingCoverage


class DocumentProcessingWorkflow:
    """Run parse, segment, LLM extraction, rules, and persistence in order."""

    def __init__(
        self,
        settings: Settings,
        *,
        llm_client: Any,
        parser: PdfParser | None = None,
    ) -> None:
        self._settings = settings
        self._llm_client = llm_client
        self._parser = parser or PdfParser()

    def process(
        self,
        session: Session,
        document_id: str,
    ) -> DocumentProcessingResult:
        """Build and atomically replace one document's Knowledge Map."""

        document_repository = DocumentRepository(session)
        document = document_repository.get(document_id)
        if document is None:
            raise AppError(
                code="DOCUMENT_NOT_FOUND",
                message="The requested document does not exist.",
                status_code=404,
                details={"document_id": document_id},
            )

        try:
            document_repository.update_status(
                document_id,
                DocumentStatus.PROCESSING,
            )
            session.commit()

            parsed = self._parser.parse(document.file_path)
            segmentation = create_candidate_segments(parsed.pages)
            document_repository.upsert_pages(document_id, parsed.pages)
            document_repository.update(
                document_id,
                page_count=parsed.page_count,
            )
            session.commit()

            knowledge_repository = KnowledgeUnitRepository(session)
            knowledge_service = KnowledgeUnitService(
                self._settings,
                llm_client=self._llm_client,
                repository=knowledge_repository,
            )
            initial_batch = knowledge_service.generate_candidates(
                document_id,
                segmentation.segments,
                min_units=3,
                max_units=10,
            )
            final_batch, validation = self._refine_until_valid(
                knowledge_service,
                initial_batch,
                segmentation,
                page_count=parsed.page_count,
            )
            records = knowledge_service.replace_map(
                document_id,
                final_batch,
                validation=validation,
            )
            ready_document = document_repository.update_status(
                document_id,
                DocumentStatus.READY,
            )
            if ready_document is None:
                raise AppError(
                    code="DOCUMENT_NOT_FOUND",
                    message="The requested document no longer exists.",
                    status_code=404,
                )
            session.commit()

            readable = set(segmentation.readable_pages)
            covered = readable.intersection(validation.coverage.covered_pages)
            ratio = len(covered) / len(readable) if readable else 0.0
            logger.info(
                "document_processed document_id=%s pages=%d units=%d "
                "coverage_ratio=%.3f",
                document_id,
                parsed.page_count,
                len(records),
                ratio,
            )
            return DocumentProcessingResult(
                document=ready_document,
                knowledge_units=tuple(records),
                coverage=ProcessingCoverage(
                    readable_pages=len(readable),
                    covered_pages=len(covered),
                    coverage_ratio=ratio,
                ),
            )
        except AppError:
            self._mark_failed(session, document_id)
            raise
        except (
            PdfParseError,
            InvalidLLMOutputError,
            LLMTimeoutError,
            LLMProviderError,
            KnowledgeUnitServiceError,
        ) as exc:
            self._mark_failed(session, document_id)
            raise self._to_app_error(exc) from exc
        except SQLAlchemyError as exc:
            self._mark_failed(session, document_id)
            logger.error(
                "document_processing_database_error document_id=%s "
                "error_type=%s",
                document_id,
                type(exc).__name__,
            )
            raise AppError(
                code="DATABASE_ERROR",
                message="Document processing could not be saved.",
                status_code=500,
            ) from exc
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            self._mark_failed(session, document_id)
            logger.error(
                "document_processing_failed document_id=%s error_type=%s",
                document_id,
                type(exc).__name__,
            )
            raise AppError(
                code="DOCUMENT_PROCESSING_FAILED",
                message="The document could not be processed.",
                status_code=500,
            ) from exc

    def _refine_until_valid(
        self,
        service: KnowledgeUnitService,
        initial_batch: KnowledgeUnitBatch,
        segmentation: SegmentationResult,
        *,
        page_count: int,
    ) -> tuple[KnowledgeUnitBatch, KnowledgeUnitBatchValidation]:
        """Apply at most the configured number of deterministic refinements."""

        batch = initial_batch
        expected_pages = set(range(1, page_count + 1))
        for refinement_round in range(
            self._settings.ku_max_refinement_rounds + 1
        ):
            validation = service.validate_batch(
                batch,
                expected_pages,
                excluded_pages=segmentation.excluded_pages,
                refinement_round=refinement_round,
                min_units=3,
                max_units=10,
            )
            if validation.is_valid:
                return batch, validation

            if not validation.coverage.is_valid:
                repaired_batch = self._repair_missing_page_coverage(
                    batch,
                    validation.coverage.missing_pages,
                    segmentation.segments,
                )
                if repaired_batch is not None:
                    repaired_validation = service.validate_batch(
                        repaired_batch,
                        expected_pages,
                        excluded_pages=segmentation.excluded_pages,
                        refinement_round=refinement_round,
                        min_units=3,
                        max_units=10,
                    )
                    if repaired_validation.is_valid:
                        logger.info(
                            "coverage_repaired_deterministically "
                            "assigned_pages=%s",
                            validation.coverage.missing_pages,
                        )
                        return repaired_batch, repaired_validation
                if (
                    refinement_round
                    >= self._settings.ku_max_refinement_rounds
                ):
                    logger.warning(
                        "coverage_refinement_exhausted "
                        "missing_pages=%s unexpected_pages=%s",
                        validation.coverage.missing_pages,
                        validation.coverage.unexpected_pages,
                    )
                    raise KnowledgeUnitServiceError(
                        "INVALID_SOURCE_COVERAGE",
                        "Knowledge Units did not cover every readable "
                        "source page after bounded refinement.",
                    )
                excluded_pages = set(segmentation.excluded_pages)
                expected_readable_pages = sorted(
                    expected_pages - excluded_pages
                )
                batch = service.refine_coverage(
                    batch.candidates,
                    segmentation.segments,
                    expected_pages=expected_readable_pages,
                    missing_pages=validation.coverage.missing_pages,
                    unexpected_pages=validation.coverage.unexpected_pages,
                    refinement_round=refinement_round + 1,
                )
                continue
            if refinement_round >= self._settings.ku_max_refinement_rounds:
                break
            if any(
                decision.action is KnowledgeUnitAction.STOP_INVALID
                for decision in validation.decisions
            ):
                break

            candidates = self._apply_rule_actions(
                service,
                batch.candidates,
                validation,
                segmentation.segments,
                refinement_round=refinement_round + 1,
            )
            if candidates is None:
                candidates = self._apply_map_level_action(
                    service,
                    batch.candidates,
                    validation,
                    segmentation.segments,
                    refinement_round=refinement_round + 1,
                )
            if candidates is None:
                break
            batch = KnowledgeUnitBatch(candidates=candidates)

        raise KnowledgeUnitServiceError(
            "NO_VALID_KNOWLEDGE_UNITS",
            "No valid Knowledge Map was produced within the refinement limit.",
        )

    @staticmethod
    def _repair_missing_page_coverage(
        batch: KnowledgeUnitBatch,
        missing_pages: Sequence[int],
        segments: Sequence[SourceSegment],
    ) -> KnowledgeUnitBatch | None:
        """Assign omitted continuation/example pages to the best existing KU.

        This fallback runs only after semantic coverage refinement is exhausted.
        A group must either share meaningful tokens with its selected KU or be
        explicitly labeled as an example/exercise continuation. It never
        invents a new unit or changes semantic content.
        """

        if not missing_pages or not batch.candidates:
            return None
        segment_by_page = {
            page: segment
            for segment in segments
            for page in segment.source_pages
        }
        original_pages = [
            set(candidate.source_pages) for candidate in batch.candidates
        ]
        updated_pages = [set(pages) for pages in original_pages]

        for group in _consecutive_page_groups(missing_pages):
            relevant_segments = [
                segment_by_page[page]
                for page in group
                if page in segment_by_page
            ]
            if len(relevant_segments) != len(group):
                return None
            group_text = "\n".join(
                f"{segment.heading or ''}\n{segment.text}"
                for segment in relevant_segments
            )
            group_tokens = _coverage_tokens(group_text)
            is_continuation = any(
                marker in group_text.casefold()
                for marker in _CONTINUATION_MARKERS
            )

            ranked: list[tuple[int, int, int]] = []
            for index, candidate in enumerate(batch.candidates):
                candidate_text = " ".join(
                    [
                        candidate.title,
                        candidate.summary,
                        *candidate.learning_objectives,
                        *candidate.key_concepts,
                    ]
                )
                overlap = len(
                    group_tokens.intersection(
                        _coverage_tokens(candidate_text)
                    )
                )
                distance = min(
                    abs(page - source_page)
                    for page in group
                    for source_page in original_pages[index]
                )
                ranked.append((overlap, -distance, -index))

            best_index = max(
                range(len(ranked)),
                key=lambda index: ranked[index],
            )
            best_overlap = ranked[best_index][0]
            if best_overlap < 2 and not is_continuation:
                return None
            updated_pages[best_index].update(group)

        repaired_candidates = [
            candidate.model_copy(
                update={"source_pages": sorted(updated_pages[index])}
            )
            for index, candidate in enumerate(batch.candidates)
        ]
        return KnowledgeUnitBatch(candidates=repaired_candidates)

    @staticmethod
    def _apply_rule_actions(
        service: KnowledgeUnitService,
        candidates: Sequence[KnowledgeUnitCandidate],
        validation: KnowledgeUnitBatchValidation,
        segments: Sequence[SourceSegment],
        *,
        refinement_round: int,
    ) -> list[KnowledgeUnitCandidate] | None:
        """Execute split/merge decisions for one complete refinement pass."""

        if not any(
            decision.action
            in {KnowledgeUnitAction.SPLIT, KnowledgeUnitAction.MERGE}
            for decision in validation.decisions
        ):
            return None

        refined: list[KnowledgeUnitCandidate] = []
        index = 0
        while index < len(candidates):
            candidate = candidates[index]
            decision = validation.decisions[index]
            if decision.action is KnowledgeUnitAction.SPLIT:
                split = service.refine_split(
                    candidate,
                    segments,
                    refinement_round=refinement_round,
                )
                refined.extend(split.candidates)
                index += 1
                continue

            if decision.action is KnowledgeUnitAction.MERGE:
                if index + 1 < len(candidates):
                    right = candidates[index + 1]
                    index += 2
                elif refined:
                    right = candidate
                    candidate = refined.pop()
                    index += 1
                else:
                    raise KnowledgeUnitServiceError(
                        "INVALID_MERGE_REFINEMENT",
                        "A lone invalid fragment has no adjacent unit to merge.",
                    )
                merged = service.refine_merge(
                    candidate,
                    right,
                    segments,
                    refinement_round=refinement_round,
                )
                refined.extend(merged.candidates)
                continue

            refined.append(candidate)
            index += 1
        return refined

    @staticmethod
    def _apply_map_level_action(
        service: KnowledgeUnitService,
        candidates: Sequence[KnowledgeUnitCandidate],
        validation: KnowledgeUnitBatchValidation,
        segments: Sequence[SourceSegment],
        *,
        refinement_round: int,
    ) -> list[KnowledgeUnitCandidate] | None:
        """Correct duplicate or out-of-range maps with a bounded semantic call."""

        if validation.duplicates.pairs and len(candidates) > 3:
            pair = validation.duplicates.pairs[0]
            left_index, right_index = pair.left_index, pair.right_index
            merged = service.refine_merge(
                candidates[left_index],
                candidates[right_index],
                segments,
                refinement_round=refinement_round,
            ).candidates[0]
            refined: list[KnowledgeUnitCandidate] = []
            for index, candidate in enumerate(candidates):
                if index == left_index:
                    refined.append(merged)
                elif index != right_index:
                    refined.append(candidate)
            return refined

        if len(candidates) < 3 and candidates:
            split_index = max(
                range(len(candidates)),
                key=lambda index: (
                    candidates[index].estimated_reading_minutes,
                    len(candidates[index].key_concepts),
                ),
            )
            split = service.refine_split(
                candidates[split_index],
                segments,
                refinement_round=refinement_round,
            )
            return [
                *candidates[:split_index],
                *split.candidates,
                *candidates[split_index + 1 :],
            ]

        if len(candidates) > 10:
            pair_index = min(
                range(len(candidates) - 1),
                key=lambda index: (
                    candidates[index].estimated_reading_minutes
                    + candidates[index + 1].estimated_reading_minutes
                ),
            )
            merged = service.refine_merge(
                candidates[pair_index],
                candidates[pair_index + 1],
                segments,
                refinement_round=refinement_round,
            )
            return [
                *candidates[:pair_index],
                *merged.candidates,
                *candidates[pair_index + 2 :],
            ]
        return None

    @staticmethod
    def _mark_failed(session: Session, document_id: str) -> None:
        """Rollback current work and persist a terminal failure when possible."""

        session.rollback()
        try:
            DocumentRepository(session).update_status(
                document_id,
                DocumentStatus.FAILED,
            )
            session.commit()
        except SQLAlchemyError as exc:
            session.rollback()
            logger.error(
                "document_failure_status_not_saved document_id=%s "
                "error_type=%s",
                document_id,
                type(exc).__name__,
            )

    @staticmethod
    def _to_app_error(exc: Exception) -> AppError:
        if isinstance(exc, PdfParseError):
            return AppError(exc.code, exc.message, status_code=422)
        if isinstance(exc, LLMTimeoutError):
            return AppError(
                "LLM_TIMEOUT",
                "The language model timed out. Please retry processing.",
                status_code=504,
            )
        if isinstance(exc, InvalidLLMOutputError):
            return AppError(
                "LLM_INVALID_OUTPUT",
                "The language model returned an invalid structured response.",
                status_code=502,
            )
        if isinstance(exc, LLMProviderError):
            return AppError(
                "LLM_PROVIDER_ERROR",
                "The language model provider request failed.",
                status_code=502,
            )
        if isinstance(exc, KnowledgeUnitServiceError):
            return AppError(
                exc.code,
                str(exc),
                status_code=422,
            )
        return AppError(
            "DOCUMENT_PROCESSING_FAILED",
            "The document could not be processed.",
            status_code=500,
        )


def _coverage_tokens(text: str) -> set[str]:
    return {
        token
        for token in _COVERAGE_TOKEN_PATTERN.findall(text.casefold())
        if len(token) > 1
        and token not in _COVERAGE_STOP_WORDS
        and not token.isdigit()
    }


def _consecutive_page_groups(
    pages: Sequence[int],
) -> list[tuple[int, ...]]:
    groups: list[list[int]] = []
    for page in sorted(set(pages)):
        if not groups or page != groups[-1][-1] + 1:
            groups.append([page])
        else:
            groups[-1].append(page)
    return [tuple(group) for group in groups]


__all__ = [
    "DocumentProcessingResult",
    "DocumentProcessingWorkflow",
    "ProcessingCoverage",
]
