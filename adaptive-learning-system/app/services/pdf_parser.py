"""Safe, page-oriented PDF text extraction with PyMuPDF."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, Final, TypeAlias

import fitz


PdfSource: TypeAlias = str | Path | bytes | bytearray | memoryview
_MAX_HEADING_CHARACTERS: Final = 160
_MAX_HEADING_WORDS: Final = 20


class PdfParseError(RuntimeError):
    """Base error carrying a stable transport-safe code and message."""

    code = "PDF_PARSE_ERROR"
    default_message = "The PDF could not be processed."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class PdfEncryptedError(PdfParseError):
    """Raised when a PDF requires a password."""

    code = "PDF_ENCRYPTED"
    default_message = "Password-protected PDFs are not supported."


class PdfEmptyError(PdfParseError):
    """Raised when a structurally valid PDF has no pages."""

    code = "PDF_EMPTY"
    default_message = "The PDF does not contain any pages."


class PdfUnreadableError(PdfParseError):
    """Raised when PyMuPDF cannot open or extract the PDF."""

    code = "PDF_UNREADABLE"
    default_message = "The PDF is invalid, damaged, or unreadable."


class PdfTextUnavailableError(PdfParseError):
    """Raised when no machine-readable text exists in the document."""

    code = "PDF_TEXT_UNAVAILABLE"
    default_message = (
        "No machine-readable text was found in the PDF. "
        "Image-only PDFs require OCR, which is outside this MVP."
    )


@dataclass(frozen=True, slots=True)
class ParsedPage:
    """Text and best-effort heading extracted from one one-based page."""

    page_number: int
    raw_text: str
    cleaned_text: str
    heading: str | None


@dataclass(frozen=True, slots=True)
class ParsedDocument:
    """Complete ordered extraction result for a PDF."""

    page_count: int
    pages: tuple[ParsedPage, ...]


@dataclass(frozen=True, slots=True)
class _HeadingCandidate:
    text: str
    font_size: float
    is_bold: bool
    top: float


def clean_pdf_text(value: str) -> str:
    """Normalize extraction noise while preserving paragraph boundaries."""

    normalized = value.replace("\x00", "").replace("\r\n", "\n").replace(
        "\r",
        "\n",
    )
    output: list[str] = []
    previous_was_blank = False

    for source_line in normalized.split("\n"):
        line = " ".join(source_line.split())
        if line:
            output.append(line)
            previous_was_blank = False
        elif output and not previous_was_blank:
            output.append("")
            previous_was_blank = True

    while output and not output[-1]:
        output.pop()
    return "\n".join(output)


def _is_heading_shape(text: str) -> bool:
    """Return whether a short text line has a plausible heading shape."""

    words = text.split()
    return (
        1 <= len(words) <= _MAX_HEADING_WORDS
        and 1 <= len(text) <= _MAX_HEADING_CHARACTERS
        and any(character.isalpha() for character in text)
    )


def _page_heading(page: fitz.Page, cleaned_text: str) -> str | None:
    """Select a prominent top-of-page line as a best-effort heading."""

    page_dict: dict[str, Any] = page.get_text("dict", sort=True)
    candidates: list[_HeadingCandidate] = []
    all_font_sizes: list[float] = []
    page_height = max(float(page.rect.height), 1.0)

    for block in page_dict.get("blocks", []):
        if block.get("type", 0) != 0:
            continue
        for line in block.get("lines", []):
            texts: list[str] = []
            sizes: list[float] = []
            is_bold = False
            for span in line.get("spans", []):
                text = clean_pdf_text(str(span.get("text", "")))
                if not text:
                    continue
                texts.append(text)
                sizes.append(float(span.get("size", 0.0)))
                is_bold = is_bold or bool(int(span.get("flags", 0)) & 16)

            text = " ".join(texts).strip()
            if not text or not sizes:
                continue
            all_font_sizes.extend(sizes)
            bbox = line.get("bbox", (0.0, 0.0, 0.0, 0.0))
            candidates.append(
                _HeadingCandidate(
                    text=text,
                    font_size=max(sizes),
                    is_bold=is_bold,
                    top=float(bbox[1]),
                )
            )

    if candidates and all_font_sizes:
        body_size = median(all_font_sizes)
        prominent = [
            candidate
            for candidate in candidates
            if candidate.top <= page_height * 0.4
            and _is_heading_shape(candidate.text)
            and (
                candidate.font_size >= body_size * 1.15
                or candidate.is_bold
            )
        ]
        if prominent:
            selected = min(
                prominent,
                key=lambda candidate: (
                    -candidate.font_size,
                    -int(candidate.is_bold),
                    candidate.top,
                ),
            )
            return selected.text

    # Some PDFs discard font metadata. A conservative first-line fallback
    # still identifies ordinary section headings without inventing text.
    first_line = next(
        (line for line in cleaned_text.splitlines() if line.strip()),
        "",
    )
    if (
        _is_heading_shape(first_line)
        and not first_line.rstrip().endswith((".", "?", "!", ";"))
    ):
        return first_line
    return None


def _open_pdf(source: PdfSource) -> fitz.Document:
    """Open a supported source without exposing its path in failures."""

    try:
        if isinstance(source, (bytes, bytearray, memoryview)):
            payload = bytes(source)
            if not payload:
                raise PdfUnreadableError()
            document = fitz.open(stream=payload, filetype="pdf")
        elif isinstance(source, (str, Path)):
            document = fitz.open(filename=str(source))
        else:
            raise TypeError("Unsupported PDF source type.")
    except PdfParseError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise PdfUnreadableError() from exc

    if not document.is_pdf:
        document.close()
        raise PdfUnreadableError()
    return document


class PdfParser:
    """Extract ordered raw and normalized text from a PDF."""

    def parse(self, source: PdfSource) -> ParsedDocument:
        """Parse ``source`` or raise a stable ``PdfParseError`` subtype."""

        document = _open_pdf(source)
        try:
            if document.needs_pass:
                raise PdfEncryptedError()
            if document.page_count == 0:
                raise PdfEmptyError()

            pages: list[ParsedPage] = []
            for page_index in range(document.page_count):
                page = document.load_page(page_index)
                raw_text = page.get_text("text", sort=True)
                cleaned_text = clean_pdf_text(raw_text)
                pages.append(
                    ParsedPage(
                        page_number=page_index + 1,
                        raw_text=raw_text,
                        cleaned_text=cleaned_text,
                        heading=_page_heading(page, cleaned_text),
                    )
                )

            if not any(page.cleaned_text for page in pages):
                raise PdfTextUnavailableError()
            return ParsedDocument(
                page_count=document.page_count,
                pages=tuple(pages),
            )
        except PdfParseError:
            raise
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            raise PdfUnreadableError() from exc
        finally:
            document.close()


def parse_pdf(source: PdfSource) -> ParsedDocument:
    """Convenience wrapper for stateless PDF parsing."""

    return PdfParser().parse(source)
