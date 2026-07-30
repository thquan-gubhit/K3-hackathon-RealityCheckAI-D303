"""Tests for deterministic page boundary detection and exclusion evidence."""

from __future__ import annotations

from app.services.document_segmentation import create_candidate_segments
from app.services.pdf_parser import ParsedPage


def _page(
    page_number: int,
    text: str,
    heading: str | None = None,
) -> ParsedPage:
    return ParsedPage(
        page_number=page_number,
        raw_text=text,
        cleaned_text=text,
        heading=heading,
    )


def test_headings_start_new_candidate_segments() -> None:
    result = create_candidate_segments(
        [
            _page(1, "First topic details.", "First topic"),
            _page(2, "Continuation without a heading."),
            _page(3, "Second topic details.", "Second topic"),
        ]
    )

    assert [segment.source_pages for segment in result.segments] == [
        (1, 2),
        (3,),
    ]
    assert [segment.segment_id for segment in result.segments] == [
        "SEG_001",
        "SEG_002",
    ]


def test_word_ceiling_and_blank_page_exclusion_are_explicit() -> None:
    result = create_candidate_segments(
        [
            _page(1, "one two three"),
            _page(2, ""),
            _page(3, "four five three"),
        ],
        max_segment_words=5,
    )

    assert [segment.source_pages for segment in result.segments] == [
        (1,),
        (3,),
    ]
    assert result.readable_pages == (1, 3)
    assert result.excluded_pages == {
        2: "No machine-readable text was found on this page."
    }


def test_short_administrative_slide_is_explicitly_excluded() -> None:
    result = create_candidate_segments(
        [
            _page(1, "Probability definitions and worked examples."),
            _page(2, "Bài tập\nteacher@example.edu.vn\n22"),
        ]
    )

    assert result.readable_pages == (1,)
    assert result.excluded_pages[2].startswith(
        "Short administrative"
    )
    assert result.segments[0].source_pages == (1,)


def test_short_academic_slide_is_not_excluded_by_word_count_alone() -> None:
    result = create_candidate_segments(
        [_page(1, "Định lý Bayes và xác suất có điều kiện.")]
    )

    assert result.readable_pages == (1,)
    assert result.excluded_pages == {}
