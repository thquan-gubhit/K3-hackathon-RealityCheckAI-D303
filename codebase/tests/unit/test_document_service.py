"""Unit tests for bounded, safe PDF upload storage."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import Base, build_engine
from app.errors import AppError
from app.models.document import Document
from app.services.document_service import DocumentService, validate_pdf_upload


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        _env_file=None,
        database_url=f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        upload_dir=tmp_path / "uploads",
        max_upload_size_mb=1,
    )


@pytest.mark.parametrize(
    ("filename", "content_type", "content", "expected_code"),
    [
        ("notes.txt", "text/plain", b"%PDF-1.7\n", "INVALID_FILE_TYPE"),
        ("notes.pdf", "text/plain", b"%PDF-1.7\n", "INVALID_FILE_TYPE"),
        ("notes.pdf", "application/pdf", b"", "EMPTY_FILE"),
        (
            "notes.pdf",
            "application/pdf",
            b"not actually a PDF",
            "INVALID_PDF_SIGNATURE",
        ),
    ],
)
def test_validate_pdf_upload_rejects_invalid_files(
    filename: str,
    content_type: str,
    content: bytes,
    expected_code: str,
) -> None:
    with pytest.raises(AppError) as captured:
        validate_pdf_upload(
            filename=filename,
            content_type=content_type,
            content=content,
            max_size_bytes=1024,
        )

    assert captured.value.code == expected_code


def test_validate_pdf_upload_rejects_oversized_content() -> None:
    with pytest.raises(AppError) as captured:
        validate_pdf_upload(
            filename="notes.pdf",
            content_type="application/pdf",
            content=b"%PDF-" + (b"x" * 20),
            max_size_bytes=10,
        )

    assert captured.value.code == "FILE_TOO_LARGE"
    assert captured.value.status_code == 413


def test_upload_uses_server_identifier_and_persists_metadata(
    tmp_path: Path,
) -> None:
    settings = _settings(tmp_path)
    engine = build_engine(settings.database_url)
    Base.metadata.create_all(engine)

    try:
        with Session(engine, expire_on_commit=False) as session:
            document = DocumentService(settings).upload(
                session,
                filename="../../Machine Learning.pdf",
                content_type="application/pdf",
                content=b"%PDF-1.7\nfixture",
            )

            stored_path = Path(document.file_path)
            assert document.filename == "Machine Learning.pdf"
            assert stored_path.parent == settings.upload_dir
            assert stored_path.name == f"{document.id}.pdf"
            assert stored_path.read_bytes() == b"%PDF-1.7\nfixture"
            assert session.get(Document, document.id) is document
    finally:
        engine.dispose()
