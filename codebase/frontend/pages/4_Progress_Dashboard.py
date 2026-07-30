"""Display mastery dimensions, evidence, and unresolved misconceptions."""

from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.api_client import BackendApiError, get_progress


def _show_misconceptions(values: Any) -> None:
    if not isinstance(values, list) or not values:
        st.caption("No active misconceptions.")
        return
    for item in values:
        if isinstance(item, dict):
            st.write(
                f"- {item.get('concept', 'Unknown')} "
                f"(count: {item.get('occurrence_count', 0)})"
            )


st.set_page_config(
    page_title="Progress Dashboard",
    page_icon="📈",
    layout="wide",
)
st.title("Progress Dashboard")
st.write(
    "Track Recall, Understanding, Application, total mastery, independent "
    "question evidence, and active misconceptions."
)

user_id = st.text_input("User ID", value="local-user")
if st.button("Load progress", type="primary"):
    try:
        with st.spinner("Loading progress..."):
            st.session_state["progress_payload"] = get_progress(user_id)
    except BackendApiError as exc:
        st.error(f"Could not load progress: {exc.message}")
        st.caption(f"Error code: {exc.code}")

payload = st.session_state.get("progress_payload")
if isinstance(payload, dict) and payload.get("user_id") == user_id:
    recommended = payload.get("recommended_next_unit_id")
    if recommended:
        st.info(f"Recommended next Knowledge Unit: {recommended}")

    units = payload.get("knowledge_units", [])
    st.subheader(f"Knowledge Units ({len(units)})")
    if not units:
        st.info("No processed Knowledge Units are available.")
    for item in units:
        if not isinstance(item, dict):
            continue
        mastery = item.get("mastery", {})
        with st.expander(
            f"{item.get('position', '?')}. {item.get('title', 'Untitled')}",
            expanded=False,
        ):
            columns = st.columns(4)
            columns[0].metric(
                "Recall",
                f"{float(mastery.get('recall_score', 0)):.0%}",
            )
            columns[1].metric(
                "Understanding",
                f"{float(mastery.get('understanding_score', 0)):.0%}",
            )
            columns[2].metric(
                "Application",
                f"{float(mastery.get('application_score', 0)):.0%}",
            )
            columns[3].metric(
                "Mastery",
                f"{float(mastery.get('mastery_score', 0)):.0%}",
            )
            st.write(f"**Status:** {mastery.get('status', 'not_started')}")
            st.write(
                "**Independent questions:** "
                f"{mastery.get('question_evidence_count', 0)}"
            )
            st.write(
                "**Answered questions:** "
                f"{item.get('answered_questions', 0)}"
            )
            st.markdown("**Active misconceptions**")
            _show_misconceptions(item.get("active_misconceptions"))
