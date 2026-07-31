"""Inspect source-grounded Knowledge Units produced from a document."""

from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.api_client import (
    BackendApiError,
    get_knowledge_map,
    get_knowledge_unit,
    list_documents,
)


def _identifier(item: dict[str, Any]) -> str:
    value = item.get("id")
    return str(value) if value is not None else ""


def _document_label(document: dict[str, Any]) -> str:
    name = (
        document.get("original_filename")
        or document.get("filename")
        or document.get("title")
        or "Untitled document"
    )
    identifier = _identifier(document)
    return f"{name} ({identifier})" if identifier else str(name)


def _show_api_error(action: str, error: BackendApiError) -> None:
    st.error(f"{action}: {error.message}")
    st.caption(f"Error code: {error.code}")


def _show_string_list(label: str, values: Any) -> None:
    st.markdown(f"**{label}**")
    if isinstance(values, list) and values:
        for value in values:
            st.write(f"- {value}")
    else:
        st.caption("None recorded.")


def _show_unit(unit: dict[str, Any]) -> None:
    unit_id = _identifier(unit) or "Unknown ID"
    title = unit.get("title") or "Untitled Knowledge Unit"
    with st.expander(f"{title} · {unit_id}", expanded=False):
        if unit.get("summary"):
            st.write(unit["summary"])

        metadata = st.columns(3)
        metadata[0].metric("Status", unit.get("status", "—"))
        metadata[1].metric(
            "Reading time",
            (
                f"{unit['estimated_reading_minutes']} min"
                if unit.get("estimated_reading_minutes") is not None
                else "—"
            ),
        )
        pages = unit.get("source_pages")
        metadata[2].metric(
            "Source pages",
            ", ".join(str(page) for page in pages)
            if isinstance(pages, list) and pages
            else "—",
        )

        first, second = st.columns(2)
        with first:
            _show_string_list(
                "Learning objectives",
                unit.get("learning_objectives"),
            )
            _show_string_list("Key concepts", unit.get("key_concepts"))
        with second:
            _show_string_list("Prerequisites", unit.get("prerequisites"))
            _show_string_list(
                "Common misconceptions",
                unit.get("common_misconceptions"),
            )

        relations = unit.get("concept_relations")
        st.markdown("**Concept relations**")
        if isinstance(relations, list) and relations:
            st.json(relations)
        else:
            st.caption("None recorded.")


st.set_page_config(
    page_title="Knowledge Map",
    page_icon="🗺️",
    layout="wide",
)

st.title("Knowledge Map")
st.write(
    "Inspect each Knowledge Unit, its objectives, concepts, prerequisites, "
    "misconceptions, and source-page traceability."
)

try:
    documents = list_documents()
except BackendApiError as exc:
    documents = []
    _show_api_error("Could not load documents", exc)

documents_by_id = {
    _identifier(document): document
    for document in documents
    if _identifier(document)
}

if not documents_by_id:
    st.info("No documents are available. Upload and process a PDF first.")
else:
    selected_document_id = st.selectbox(
        "Document",
        options=list(documents_by_id),
        format_func=lambda identifier: _document_label(
            documents_by_id[identifier]
        ),
    )

    if st.button("Load Knowledge Map", type="primary"):
        try:
            with st.spinner("Loading Knowledge Map..."):
                knowledge_map = get_knowledge_map(selected_document_id)
        except BackendApiError as exc:
            _show_api_error("Could not load Knowledge Map", exc)
        else:
            st.session_state["knowledge_map"] = knowledge_map

    knowledge_map = st.session_state.get("knowledge_map")
    if (
        isinstance(knowledge_map, dict)
        and str(knowledge_map.get("document_id", selected_document_id))
        == selected_document_id
    ):
        status = knowledge_map.get("status")
        if status:
            st.caption(f"Map status: {status}")

        units = knowledge_map.get("knowledge_units", [])
        st.subheader(f"Knowledge Units ({len(units)})")
        if not units:
            st.info(
                "This document has no Knowledge Units yet. Process it from "
                "the Upload Document page."
            )
        else:
            for unit in units:
                _show_unit(unit)

            unit_ids = [
                _identifier(unit) for unit in units if _identifier(unit)
            ]
            if unit_ids:
                st.divider()
                st.subheader("Knowledge Unit detail")
                selected_unit_id = st.selectbox(
                    "Knowledge Unit",
                    options=unit_ids,
                    format_func=lambda unit_id: next(
                        (
                            f"{unit.get('title', 'Untitled')} ({unit_id})"
                            for unit in units
                            if _identifier(unit) == unit_id
                        ),
                        unit_id,
                    ),
                )
                if st.button("Refresh unit detail"):
                    try:
                        with st.spinner("Loading Knowledge Unit..."):
                            detail = get_knowledge_unit(selected_unit_id)
                    except BackendApiError as exc:
                        _show_api_error(
                            "Could not load Knowledge Unit",
                            exc,
                        )
                    else:
                        st.session_state["knowledge_unit_detail"] = detail

                detail = st.session_state.get("knowledge_unit_detail")
                if (
                    isinstance(detail, dict)
                    and _identifier(detail) == selected_unit_id
                ):
                    _show_unit(detail)
