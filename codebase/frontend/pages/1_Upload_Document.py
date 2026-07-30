"""Upload and process PDF documents through the FastAPI backend."""

from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.api_client import (
    BackendApiError,
    list_documents,
    process_document,
    upload_document,
)


def _document_id(document: dict[str, Any]) -> str:
    value = document.get("id")
    return str(value) if value is not None else ""


def _document_label(document: dict[str, Any]) -> str:
    name = (
        document.get("original_filename")
        or document.get("filename")
        or document.get("title")
        or "Untitled document"
    )
    identifier = _document_id(document)
    status = document.get("status")
    suffix = f" · {status}" if status else ""
    return f"{name} ({identifier}){suffix}" if identifier else f"{name}{suffix}"


def _show_api_error(action: str, error: BackendApiError) -> None:
    st.error(f"{action}: {error.message}")
    st.caption(f"Error code: {error.code}")


def _show_document_summary(document: dict[str, Any]) -> None:
    st.write(f"**Document ID:** {_document_id(document) or 'Unavailable'}")
    name = (
        document.get("original_filename")
        or document.get("filename")
        or document.get("title")
    )
    if name:
        st.write(f"**File:** {name}")
    if document.get("status"):
        st.write(f"**Status:** {document['status']}")
    page_count = document.get("page_count")
    if page_count is not None:
        st.write(f"**Pages:** {page_count}")


st.set_page_config(
    page_title="Upload Document",
    page_icon="📄",
    layout="wide",
)

st.title("Upload Document")
st.write(
    "Upload one text-based PDF, then ask the backend to extract pages and "
    "build its Knowledge Map."
)

st.subheader("1. Upload a PDF")
uploaded_file = st.file_uploader(
    "Choose a PDF",
    type=["pdf"],
    accept_multiple_files=False,
    help="The backend validates file type and configured size limits.",
)

if st.button(
    "Upload PDF",
    type="primary",
    disabled=uploaded_file is None,
    use_container_width=False,
):
    if uploaded_file is not None:
        try:
            with st.spinner("Uploading PDF..."):
                uploaded_document = upload_document(
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    content_type=uploaded_file.type or "application/pdf",
                )
        except BackendApiError as exc:
            _show_api_error("Upload failed", exc)
        else:
            st.session_state["last_uploaded_document"] = uploaded_document
            st.success("PDF uploaded successfully.")
            _show_document_summary(uploaded_document)

st.divider()
st.subheader("2. Process a document")

documents: list[dict[str, Any]] = []
try:
    documents = list_documents()
except BackendApiError as exc:
    _show_api_error("Could not load documents", exc)

last_uploaded = st.session_state.get("last_uploaded_document")
if isinstance(last_uploaded, dict) and _document_id(last_uploaded):
    known_ids = {_document_id(document) for document in documents}
    if _document_id(last_uploaded) not in known_ids:
        documents = [last_uploaded, *documents]

documents_by_id = {
    _document_id(document): document
    for document in documents
    if _document_id(document)
}

if not documents_by_id:
    st.info("No documents are available yet. Upload a PDF to continue.")
else:
    selected_id = st.selectbox(
        "Document",
        options=list(documents_by_id),
        format_func=lambda identifier: _document_label(
            documents_by_id[identifier]
        ),
    )
    _show_document_summary(documents_by_id[selected_id])

    if st.button("Process selected document", type="primary"):
        try:
            with st.spinner(
                "Extracting pages and building Knowledge Units. "
                "This can take a moment..."
            ):
                result = process_document(selected_id)
        except BackendApiError as exc:
            _show_api_error("Processing failed", exc)
        else:
            st.session_state["last_processing_result"] = result
            st.success("Document processing completed.")

    processing_result = st.session_state.get("last_processing_result")
    if (
        isinstance(processing_result, dict)
        and _document_id(processing_result.get("document", {})) == selected_id
    ):
        units = processing_result.get("knowledge_units", [])
        coverage = processing_result.get("coverage", {})
        st.subheader("Processing result")
        metric_columns = st.columns(4)
        metric_columns[0].metric("Knowledge Units", len(units))
        metric_columns[1].metric(
            "Readable pages",
            coverage.get("readable_pages", "—"),
        )
        metric_columns[2].metric(
            "Covered pages",
            coverage.get("covered_pages", "—"),
        )
        ratio = coverage.get("coverage_ratio")
        ratio_label = f"{ratio:.0%}" if isinstance(ratio, (int, float)) else "—"
        metric_columns[3].metric("Coverage", ratio_label)
        st.info("Open the Knowledge Map page to inspect the generated units.")
