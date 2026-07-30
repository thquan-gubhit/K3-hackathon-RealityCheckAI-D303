"""Deterministic page-to-segment boundary detection for KU extraction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Sequence

from app.services.knowledge_unit_service import SourceSegment
from app.services.pdf_parser import ParsedPage


DEFAULT_MAX_SEGMENT_WORDS: Final = 1_200


@dataclass(frozen=True, slots=True)
class SegmentationResult:
    """Candidate segments plus explicit evidence for blank-page exclusion."""

    segments: tuple[SourceSegment, ...]
    readable_pages: tuple[int, ...]
    excluded_pages: dict[int, str]


def create_candidate_segments(
    pages: Sequence[ParsedPage],
    *,
    max_segment_words: int = DEFAULT_MAX_SEGMENT_WORDS,
) -> SegmentationResult:
    """Group consecutive pages, splitting at headings and a word ceiling.

    Headings are the primary topic-boundary signal. Pages without a detected
    heading remain attached to the preceding topic until the deterministic
    size ceiling is reached. Blank pages are never silently discarded: their
    one-based page numbers and exclusion reason are returned for coverage
    validation.
    """

    if max_segment_words < 1:
        raise ValueError("max_segment_words must be positive")

    readable_pages: list[int] = []
    excluded_pages: dict[int, str] = {}
    segments: list[SourceSegment] = []
    current_pages: list[int] = []
    current_text: list[str] = []
    current_heading: str | None = None
    current_word_count = 0

    def flush() -> None:
        nonlocal current_heading, current_word_count
        if not current_pages:
            return
        segments.append(
            SourceSegment(
                segment_id=f"SEG_{len(segments) + 1:03d}",
                source_pages=tuple(current_pages),
                text="\n\n".join(current_text),
                heading=current_heading,
            )
        )
        current_pages.clear()
        current_text.clear()
        current_heading = None
        current_word_count = 0

    for page in sorted(pages, key=lambda item: item.page_number):
        text = page.cleaned_text.strip()
        if not text:
            excluded_pages[page.page_number] = (
                "No machine-readable text was found on this page."
            )
            continue

        readable_pages.append(page.page_number)
        page_word_count = len(text.split())
        starts_new_topic = bool(page.heading and current_pages)
        exceeds_size = bool(
            current_pages
            and current_word_count + page_word_count > max_segment_words
        )
        if starts_new_topic or exceeds_size:
            flush()

        if not current_pages:
            current_heading = page.heading
        current_pages.append(page.page_number)
        current_text.append(text)
        current_word_count += page_word_count

    flush()
    if not segments:
        raise ValueError("at least one readable page is required")

    return SegmentationResult(
        segments=tuple(segments),
        readable_pages=tuple(readable_pages),
        excluded_pages=excluded_pages,
    )


__all__ = [
    "DEFAULT_MAX_SEGMENT_WORDS",
    "SegmentationResult",
    "create_candidate_segments",
]
