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
st.subheader("MVP learning loop")
st.write(
    "Upload and process a PDF, inspect its Knowledge Map, start an adaptive "
    "study session, and review mastery in the Progress Dashboard."
)
