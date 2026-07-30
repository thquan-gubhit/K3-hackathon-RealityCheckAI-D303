"""SQLAlchemy persistence operations for documents and extracted pages."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Protocol

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.document import (
    Document,
    DocumentPage,
    DocumentStatus,
    utc_now,
)


class PagePayload(Protocol):
    """Structural input accepted from parser or Pydantic page schemas."""

    page_number: int
    raw_text: str
    cleaned_text: str
    heading: str | None


class DocumentNotFoundError(LookupError):
    """Raised when a write targets an unknown document."""

    code = "DOCUMENT_NOT_FOUND"

    def __init__(self, document_id: str) -> None:
        self.document_id = document_id
        super().__init__("The requested document does not exist.")


class DocumentRepository:
    """Transaction-neutral repository.

    Methods flush pending changes so generated identifiers and constraints are
    visible immediately. The owning workflow decides when to commit or roll
    back the transaction.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        filename: str,
        file_path: str,
        page_count: int = 0,
        status: DocumentStatus | str = DocumentStatus.UPLOADED,
        document_id: str | None = None,
    ) -> Document:
        """Create and flush one document record."""

        if page_count < 0:
            raise ValueError("page_count must be non-negative")
        document = Document(
            filename=filename,
            file_path=file_path,
            page_count=page_count,
            status=DocumentStatus(status),
        )
        if document_id is not None:
            document.id = document_id
        self.session.add(document)
        self.session.flush()
        return document

    def get(self, document_id: str) -> Document | None:
        """Return a document by identifier, or ``None``."""

        return self.session.get(Document, document_id)

    def get_with_pages(self, document_id: str) -> Document | None:
        """Return one document with pages loaded in page-number order."""

        statement = (
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.pages))
        )
        document = self.session.scalar(statement)
        if document is not None:
            document.pages.sort(key=lambda page: page.page_number)
        return document

    def list_documents(
        self,
        *,
        status: DocumentStatus | str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Document]:
        """List documents newest first with optional status filtering."""

        if offset < 0:
            raise ValueError("offset must be non-negative")
        if limit < 1:
            raise ValueError("limit must be positive")

        statement = select(Document)
        if status is not None:
            statement = statement.where(
                Document.status == DocumentStatus(status)
            )
        statement = statement.order_by(
            Document.created_at.desc(),
            Document.id.desc(),
        )
        statement = statement.offset(offset).limit(limit)
        return list(self.session.scalars(statement).all())

    def count(
        self,
        *,
        status: DocumentStatus | str | None = None,
    ) -> int:
        """Count documents with optional status filtering."""

        statement = select(func.count()).select_from(Document)
        if status is not None:
            statement = statement.where(
                Document.status == DocumentStatus(status)
            )
        return int(self.session.scalar(statement) or 0)

    def update(
        self,
        document_id: str,
        *,
        filename: str | None = None,
        file_path: str | None = None,
        page_count: int | None = None,
    ) -> Document | None:
        """Update mutable document metadata and flush the row."""

        document = self.get(document_id)
        if document is None:
            return None
        if filename is not None:
            document.filename = filename
        if file_path is not None:
            document.file_path = file_path
        if page_count is not None:
            if page_count < 0:
                raise ValueError("page_count must be non-negative")
            document.page_count = page_count
        self.session.flush()
        return document

    def update_status(
        self,
        document_id: str,
        status: DocumentStatus | str,
        *,
        processed_at: datetime | None = None,
    ) -> Document | None:
        """Set lifecycle status and maintain its completion timestamp."""

        document = self.get(document_id)
        if document is None:
            return None

        normalized_status = DocumentStatus(status)
        document.status = normalized_status
        if normalized_status in {
            DocumentStatus.READY,
            DocumentStatus.FAILED,
        }:
            document.processed_at = processed_at or utc_now()
        else:
            document.processed_at = None
        self.session.flush()
        return document

    def upsert_pages(
        self,
        document_id: str,
        pages: Iterable[PagePayload],
    ) -> list[DocumentPage]:
        """Insert or update pages by ``(document_id, page_number)``."""

        document = self.get(document_id)
        if document is None:
            raise DocumentNotFoundError(document_id)

        payloads = list(pages)
        page_numbers = [payload.page_number for payload in payloads]
        if any(page_number < 1 for page_number in page_numbers):
            raise ValueError("page_number must be positive")
        if len(set(page_numbers)) != len(page_numbers):
            raise ValueError("page_number values must be unique per batch")
        if not payloads:
            return []

        existing_statement = select(DocumentPage).where(
            DocumentPage.document_id == document_id,
            DocumentPage.page_number.in_(page_numbers),
        )
        existing = {
            page.page_number: page
            for page in self.session.scalars(existing_statement).all()
        }
        persisted: list[DocumentPage] = []

        for payload in sorted(payloads, key=lambda item: item.page_number):
            page = existing.get(payload.page_number)
            if page is None:
                page = DocumentPage(
                    document_id=document_id,
                    page_number=payload.page_number,
                )
                self.session.add(page)
            page.raw_text = payload.raw_text
            page.cleaned_text = payload.cleaned_text
            page.heading = payload.heading
            persisted.append(page)

        document.page_count = max(document.page_count, max(page_numbers))
        self.session.flush()
        return persisted

    def delete(self, document_id: str) -> bool:
        """Explicitly delete a document and its pages."""

        document = self.get(document_id)
        if document is None:
            return False
        self.session.execute(
            delete(DocumentPage).where(
                DocumentPage.document_id == document_id
            )
        )
        self.session.delete(document)
        self.session.flush()
        return True
