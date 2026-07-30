"""Pydantic contracts for document persistence and API responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.document import DocumentStatus
from app.schemas.knowledge_unit import KnowledgeUnitResponse


class DocumentPageCreate(BaseModel):
    """Validated page text ready for persistence."""

    page_number: int = Field(ge=1)
    raw_text: str
    cleaned_text: str
    heading: str | None = Field(default=None, max_length=500)

    @field_validator("heading")
    @classmethod
    def normalize_heading(cls, value: str | None) -> str | None:
        """Store blank headings as null."""

        if value is None:
            return None
        normalized = " ".join(value.split())
        return normalized or None


class DocumentResponse(BaseModel):
    """Public document metadata.

    ``file_path`` is intentionally absent because storage locations are an
    internal implementation detail.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    page_count: int = Field(ge=0)
    status: DocumentStatus
    created_at: datetime
    processed_at: datetime | None


class DocumentPageResponse(BaseModel):
    """Public page-level extraction result."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    page_number: int = Field(ge=1)
    raw_text: str
    cleaned_text: str
    heading: str | None


class DocumentDetailResponse(DocumentResponse):
    """Document metadata with its ordered extracted pages."""

    pages: list[DocumentPageResponse] = Field(default_factory=list)


class DocumentListResponse(BaseModel):
    """Stable envelope for paginated document listings."""

    items: list[DocumentResponse]
    total: int = Field(ge=0)


class ProcessingCoverageResponse(BaseModel):
    """Page coverage summary for one completed processing request."""

    model_config = ConfigDict(from_attributes=True)

    readable_pages: int = Field(ge=0)
    covered_pages: int = Field(ge=0)
    coverage_ratio: float = Field(ge=0.0, le=1.0)


class DocumentProcessingResponse(BaseModel):
    """Direct synchronous result of the Phase 2 processing workflow."""

    document: DocumentResponse
    knowledge_units: list[KnowledgeUnitResponse]
    coverage: ProcessingCoverageResponse


class KnowledgeMapResponse(BaseModel):
    """Ordered validated Knowledge Units for one ready document."""

    document_id: str
    status: DocumentStatus
    knowledge_units: list[KnowledgeUnitResponse]
