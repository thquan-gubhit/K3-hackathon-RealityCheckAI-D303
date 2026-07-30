"""Load bounded source text for a persisted Knowledge Unit."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.knowledge_unit import KnowledgeUnit
from app.repositories.document_repository import DocumentRepository


class SourceContextError(RuntimeError):
    """Raised when persisted source evidence is missing."""


def build_unit_source_context(
    session: Session,
    unit: KnowledgeUnit,
) -> str:
    """Return ordered page text limited to the unit's source pages."""

    document = DocumentRepository(session).get_with_pages(unit.document_id)
    if document is None:
        raise SourceContextError("The source document does not exist.")
    expected = set(unit.source_pages)
    sections = [
        f"[Page {page.page_number}]\n{page.cleaned_text}"
        for page in document.pages
        if page.page_number in expected and page.cleaned_text.strip()
    ]
    if not sections:
        raise SourceContextError(
            "No readable source context exists for this Knowledge Unit."
        )
    return "\n\n".join(sections)


__all__ = ["SourceContextError", "build_unit_source_context"]
