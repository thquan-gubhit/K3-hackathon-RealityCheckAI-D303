"""Document upload, processing, and Knowledge Map endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.api.dependencies import LLMDependency, SettingsDependency
from app.database import get_db
from app.errors import AppError
from app.models.document import DocumentStatus
from app.repositories.document_repository import DocumentRepository
from app.repositories.knowledge_unit_repository import KnowledgeUnitRepository
from app.schemas.document import (
    DocumentProcessingResponse,
    DocumentResponse,
    KnowledgeMapResponse,
)
from app.services.document_service import DocumentService
from app.workflows.document_processing import DocumentProcessingWorkflow


router = APIRouter(prefix="/documents", tags=["documents"])
DatabaseDependency = Annotated[Session, Depends(get_db)]


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=201,
    summary="Upload one validated PDF",
)
async def upload_document(
    settings: SettingsDependency,
    session: DatabaseDependency,
    file: Annotated[UploadFile, File(...)],
) -> DocumentResponse:
    """Validate size/type, store with a server ID, and persist metadata."""

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    content = await file.read(max_bytes + 1)
    document = DocumentService(settings).upload(
        session,
        filename=file.filename,
        content_type=file.content_type,
        content=content,
    )
    return DocumentResponse.model_validate(document)


@router.post(
    "/{document_id}/process",
    response_model=DocumentProcessingResponse,
    summary="Build and persist a document Knowledge Map",
)
def process_document(
    document_id: str,
    settings: SettingsDependency,
    llm_client: LLMDependency,
    session: DatabaseDependency,
) -> DocumentProcessingResponse:
    """Run the bounded synchronous Phase 2 workflow."""

    result = DocumentProcessingWorkflow(
        settings,
        llm_client=llm_client,
    ).process(session, document_id)
    return DocumentProcessingResponse(
        document=result.document,
        knowledge_units=list(result.knowledge_units),
        coverage=result.coverage,
    )


@router.get(
    "",
    response_model=list[DocumentResponse],
    summary="List uploaded documents",
)
def list_documents(
    session: DatabaseDependency,
    status: DocumentStatus | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
) -> list[DocumentResponse]:
    records = DocumentRepository(session).list_documents(
        status=status,
        offset=offset,
        limit=limit,
    )
    return [DocumentResponse.model_validate(record) for record in records]


@router.get(
    "/{document_id}/knowledge-map",
    response_model=KnowledgeMapResponse,
    summary="Return a validated Knowledge Map",
)
def get_knowledge_map(
    document_id: str,
    session: DatabaseDependency,
) -> KnowledgeMapResponse:
    document = DocumentRepository(session).get(document_id)
    if document is None:
        raise AppError(
            "DOCUMENT_NOT_FOUND",
            "The requested document does not exist.",
            status_code=404,
            details={"document_id": document_id},
        )
    if document.status is not DocumentStatus.READY:
        raise AppError(
            "KNOWLEDGE_MAP_NOT_READY",
            "Process the document successfully before loading its Knowledge Map.",
            status_code=409,
            details={"document_status": document.status.value},
        )

    units = KnowledgeUnitRepository(session).list_for_document(document_id)
    return KnowledgeMapResponse(
        document_id=document.id,
        status=document.status,
        knowledge_units=units,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Return document metadata",
)
def get_document(
    document_id: str,
    session: DatabaseDependency,
) -> DocumentResponse:
    document = DocumentRepository(session).get(document_id)
    if document is None:
        raise AppError(
            "DOCUMENT_NOT_FOUND",
            "The requested document does not exist.",
            status_code=404,
            details={"document_id": document_id},
        )
    return DocumentResponse.model_validate(document)
