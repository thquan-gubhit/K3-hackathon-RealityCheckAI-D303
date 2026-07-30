"""Home page for the Adaptive Learning System Streamlit application."""

from __future__ import annotations

import streamlit as st

from frontend.api_client import check_backend_health


st.set_page_config(
    page_title="Adaptive Learning System",
    page_icon="🧠",
    layout="centered",
)

st.title("Adaptive Learning System")
st.write(
    "Turn learning materials into focused active-recall sessions and track "
    "your progress over time."
)

st.subheader("System status")
health = check_backend_health()

if health.available:
    st.success(health.message)
    if health.payload and health.payload.get("app_name"):
        st.caption(f"Connected to {health.payload['app_name']}.")
else:
    st.warning(health.message)
    st.info(
        "Start the FastAPI backend, then reload this page. "
        "If it runs at a different address, set BACKEND_API_URL in your environment."
    )

st.divider()
st.subheader("Phase 1 foundation")
st.write(
    "The application shell is ready. Document upload, knowledge maps, study "
    "sessions, and progress views will be added in later phases."
)
