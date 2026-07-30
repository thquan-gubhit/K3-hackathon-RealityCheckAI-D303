"""Unit tests for safe page-level PDF parsing."""

from __future__ import annotations

import fitz
import pytest

from app.services.pdf_parser import (
    PdfEmptyError,
    PdfEncryptedError,
    PdfParser,
    PdfTextUnavailableError,
    PdfUnreadableError,
    clean_pdf_text,
)


def _text_pdf() -> bytes:
    document = fitz.open()
    try:
        first_page = document.new_page()
        first_page.insert_text(
            (72, 72),
            "Overfitting and Generalization",
            fontsize=18,
        )
        first_page.insert_text(
            (72, 110),
            "Training performance can diverge from validation performance.",
            fontsize=11,
        )
        second_page = document.new_page()
        second_page.insert_text(
            (72, 72),
            "Regularization",
            fontsize=18,
        )
        second_page.insert_text(
            (72, 110),
            "Regularization can reduce model complexity.",
            fontsize=11,
        )
        return document.tobytes()
    finally:
        document.close()


def _blank_pdf() -> bytes:
    document = fitz.open()
    try:
        document.new_page()
        return document.tobytes()
    finally:
        document.close()


def _encrypted_pdf() -> bytes:
    document = fitz.open()
    try:
        page = document.new_page()
        page.insert_text((72, 72), "Protected content")
        return document.tobytes(
            encryption=fitz.PDF_ENCRYPT_AES_256,
            owner_pw="owner-password",
            user_pw="user-password",
        )
    finally:
        document.close()


def test_parse_extracts_raw_cleaned_text_heading_and_page_numbers() -> None:
    result = PdfParser().parse(_text_pdf())

    assert result.page_count == 2
    assert tuple(page.page_number for page in result.pages) == (1, 2)
    assert "Overfitting" in result.pages[0].raw_text
    assert "validation performance" in result.pages[0].cleaned_text
    assert result.pages[0].heading == "Overfitting and Generalization"
    assert result.pages[1].heading == "Regularization"


def test_clean_pdf_text_normalizes_noise_but_keeps_paragraph_breaks() -> None:
    assert clean_pdf_text(
        "  first   line \r\n\r\n\r\n second\x00 line  \n"
    ) == "first line\n\nsecond line"


def test_parse_rejects_encrypted_pdf_with_stable_error() -> None:
    with pytest.raises(PdfEncryptedError) as captured:
        PdfParser().parse(_encrypted_pdf())

    assert captured.value.code == "PDF_ENCRYPTED"
    assert "password" in captured.value.message.lower()


def test_parse_rejects_image_only_or_blank_pdf() -> None:
    with pytest.raises(PdfTextUnavailableError) as captured:
        PdfParser().parse(_blank_pdf())

    assert captured.value.code == "PDF_TEXT_UNAVAILABLE"
    assert "OCR" in captured.value.message


def test_parse_rejects_zero_page_pdf(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class EmptyPdf:
        is_pdf = True
        needs_pass = False
        page_count = 0

        def close(self) -> None:
            return None

    monkeypatch.setattr(
        "app.services.pdf_parser.fitz.open",
        lambda **_: EmptyPdf(),
    )

    with pytest.raises(PdfEmptyError) as captured:
        PdfParser().parse(b"%PDF empty fixture")

    assert captured.value.code == "PDF_EMPTY"


@pytest.mark.parametrize("source", [b"", b"not a PDF"])
def test_parse_rejects_unreadable_input(source: bytes) -> None:
    with pytest.raises(PdfUnreadableError) as captured:
        PdfParser().parse(source)

    assert captured.value.code == "PDF_UNREADABLE"
