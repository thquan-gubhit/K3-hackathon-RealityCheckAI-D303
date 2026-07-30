"""Document upload validation and durable local storage."""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import Settings
from app.errors import AppError
from app.models.document import Document, DocumentStatus, new_uuid
from app.repositories.document_repository import DocumentRepository


logger = logging.getLogger(__name__)

_ALLOWED_PDF_MEDIA_TYPES = {
    "",
    "application/octet-stream",
    "application/pdf",
    "application/x-pdf",
}


def normalize_upload_filename(filename: str | None) -> str:
    """Return a safe basename while rejecting unusable client filenames."""

    if filename is None:
        raise AppError(
            code="INVALID_FILENAME",
            message="The uploaded PDF must have a filename.",
        )

    # Browsers normally send a basename, but older clients may include a
    # Windows or POSIX path. Only the final component is ever retained.
    basename = filename.replace("\\", "/").rsplit("/", 1)[-1].strip()
    if (
        not basename
        or basename in {".", ".."}
        or any(ord(character) < 32 for character in basename)
        or len(basename) > 255
    ):
        raise AppError(
            code="INVALID_FILENAME",
            message="The uploaded PDF has an invalid filename.",
        )
    return basename


def validate_pdf_upload(
    *,
    filename: str | None,
    content_type: str | None,
    content: bytes,
    max_size_bytes: int,
) -> str:
    """Validate one upload and return its normalized display filename."""

    safe_filename = normalize_upload_filename(filename)
    if Path(safe_filename).suffix.casefold() != ".pdf":
        raise AppError(
            code="INVALID_FILE_TYPE",
            message="Only PDF files are supported.",
            details={"allowed_extension": ".pdf"},
        )

    normalized_media_type = (content_type or "").split(";", 1)[0].strip().lower()
    if normalized_media_type not in _ALLOWED_PDF_MEDIA_TYPES:
        raise AppError(
            code="INVALID_FILE_TYPE",
            message="Only PDF files are supported.",
            details={"allowed_media_type": "application/pdf"},
        )

    if not content:
        raise AppError(
            code="EMPTY_FILE",
            message="The uploaded PDF is empty.",
        )
    if len(content) > max_size_bytes:
        raise AppError(
            code="FILE_TOO_LARGE",
            message="The uploaded PDF exceeds the configured size limit.",
            status_code=413,
            details={"max_size_bytes": max_size_bytes},
        )
    if not content.startswith(b"%PDF-"):
        raise AppError(
            code="INVALID_PDF_SIGNATURE",
            message="The uploaded file is not a valid PDF.",
        )
    return safe_filename


class DocumentService:
    """Application service for validated, transaction-safe PDF uploads."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def max_size_bytes(self) -> int:
        """Return the configured binary upload limit."""

        return self.settings.max_upload_size_mb * 1024 * 1024

    def upload(
        self,
        session: Session,
        *,
        filename: str | None,
        content_type: str | None,
        content: bytes,
    ) -> Document:
        """Validate, store, and persist one uploaded PDF atomically."""

        safe_filename = validate_pdf_upload(
            filename=filename,
            content_type=content_type,
            content=content,
            max_size_bytes=self.max_size_bytes,
        )

        upload_root = self.settings.upload_dir.resolve()
        document_id = new_uuid()
        destination = (upload_root / f"{document_id}.pdf").resolve()
        temporary = (
            upload_root / f".{document_id}.{uuid4().hex}.uploading"
        ).resolve()
        if destination.parent != upload_root or temporary.parent != upload_root:
            raise AppError(
                code="INVALID_STORAGE_PATH",
                message="The upload storage path is invalid.",
                status_code=500,
            )

        repository = DocumentRepository(session)
        try:
            upload_root.mkdir(parents=True, exist_ok=True)
            temporary.write_bytes(content)
            temporary.replace(destination)
            document = repository.create(
                filename=safe_filename,
                file_path=str(destination),
                status=DocumentStatus.UPLOADED,
                document_id=document_id,
            )
            session.commit()
            session.refresh(document)
            logger.info(
                "document_uploaded document_id=%s size_bytes=%s",
                document.id,
                len(content),
            )
            return document
        except OSError as exc:
            session.rollback()
            self._remove_partial_files(temporary, destination)
            logger.error(
                "document_storage_failed document_id=%s error_type=%s",
                document_id,
                type(exc).__name__,
            )
            raise AppError(
                code="FILE_STORAGE_ERROR",
                message="The PDF could not be stored. Please try again.",
                status_code=500,
            ) from exc
        except SQLAlchemyError as exc:
            session.rollback()
            self._remove_partial_files(temporary, destination)
            logger.error(
                "document_persistence_failed document_id=%s error_type=%s",
                document_id,
                type(exc).__name__,
            )
            raise AppError(
                code="DATABASE_ERROR",
                message="The document metadata could not be saved.",
                status_code=500,
            ) from exc

    @staticmethod
    def _remove_partial_files(*paths: Path) -> None:
        """Best-effort cleanup restricted to already-resolved upload files."""

        for path in paths:
            try:
                path.unlink(missing_ok=True)
            except OSError as exc:
                logger.warning(
                    "document_cleanup_failed file_name=%s error_type=%s",
                    path.name,
                    type(exc).__name__,
                )


__all__ = [
    "DocumentService",
    "normalize_upload_filename",
    "validate_pdf_upload",
]
