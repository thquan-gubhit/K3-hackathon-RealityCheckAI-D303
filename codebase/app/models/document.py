"""Document and page-level persistence models."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Final
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


UUID_LENGTH: Final = 36


def new_uuid() -> str:
    """Return a portable UUID string for SQLite-backed identifiers."""

    return str(uuid4())


def utc_now() -> datetime:
    """Return an aware UTC timestamp for Python-side defaults."""

    return datetime.now(timezone.utc)


class DocumentStatus(StrEnum):
    """Lifecycle states for an uploaded document."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class Document(Base):
    """Metadata for one server-managed PDF."""

    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("page_count >= 0", name="ck_documents_page_count"),
    )

    id: Mapped[str] = mapped_column(
        String(UUID_LENGTH),
        primary_key=True,
        default=new_uuid,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    page_count: Mapped[int] = mapped_column(nullable=False, default=0)
    status: Mapped[DocumentStatus] = mapped_column(
        SqlEnum(
            DocumentStatus,
            native_enum=False,
            values_callable=lambda statuses: [status.value for status in statuses],
            validate_strings=True,
            length=32,
            name="document_status",
        ),
        nullable=False,
        default=DocumentStatus.UPLOADED,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    pages: Mapped[list["DocumentPage"]] = relationship(
        back_populates="document",
        lazy="selectin",
        order_by="DocumentPage.page_number",
    )

    def __repr__(self) -> str:
        """Represent metadata without exposing its server-side path."""

        status = (
            self.status.value
            if isinstance(self.status, DocumentStatus)
            else self.status
        )
        return (
            f"Document(id={self.id!r}, filename={self.filename!r}, "
            f"status={status!r})"
        )


class DocumentPage(Base):
    """Raw and normalized text extracted from one PDF page."""

    __tablename__ = "document_pages"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "page_number",
            name="uq_document_pages_document_page",
        ),
        CheckConstraint(
            "page_number >= 1",
            name="ck_document_pages_page_number",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(UUID_LENGTH),
        primary_key=True,
        default=new_uuid,
    )
    document_id: Mapped[str] = mapped_column(
        String(UUID_LENGTH),
        ForeignKey("documents.id"),
        nullable=False,
        index=True,
    )
    page_number: Mapped[int] = mapped_column(nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    cleaned_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    heading: Mapped[str | None] = mapped_column(String(500), nullable=True)

    document: Mapped[Document] = relationship(back_populates="pages")

    def __repr__(self) -> str:
        """Represent page identity without emitting document contents."""

        return (
            f"DocumentPage(id={self.id!r}, document_id={self.document_id!r}, "
            f"page_number={self.page_number!r})"
        )
