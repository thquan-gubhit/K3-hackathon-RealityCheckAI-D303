"""Home page for the Adaptive Learning System Streamlit application."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from frontend.api_client import check_backend_health

_CSS_PATH = Path(__file__).resolve().parent / "style.css"

st.set_page_config(
    page_title="Adaptive Learning System",
    page_icon="🧠",
    layout="centered",
)

# Inject custom CSS
if _CSS_PATH.exists():
    st.markdown(
        f"<style>{_CSS_PATH.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

st.markdown(
    '<h1 style="font-family:Inter,sans-serif;'
    "background:linear-gradient(135deg,#7c5cfc 0%,#5ce1e6 100%);"
    "-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
    'background-clip:text">🧠 Adaptive Learning System</h1>',
    unsafe_allow_html=True,
)
st.caption(
    "Biến tài liệu học tập thành phiên kiểm tra kiến thức chủ động "
    "(Active Recall) và theo dõi tiến độ theo thời gian."
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
st.markdown(
    '<div class="glass-card">'
    '<div class="section-header">🎓 Bắt đầu nhanh — Slide Learning</div>'
    '<div class="feedback-text">'
    "Mở trang <b>Slide Learning</b> ở sidebar bên trái để trải nghiệm "
    "luồng học tập chính:<br>"
    "📄 Upload PDF → 📖 Đọc Slide → 🔒 Che Slide → "
    "🧠 Tự Giải thích → 📊 AI Đánh giá → ✅ Master"
    "</div></div>",
    unsafe_allow_html=True,
)

st.markdown("")
st.markdown(
    '<div class="glass-card">'
    '<div class="section-header">📚 Các trang phụ</div>'
    '<div class="feedback-text">'
    "• <b>Upload Document</b> — Upload và xử lý PDF thủ công<br>"
    "• <b>Knowledge Map</b> — Xem chi tiết Knowledge Units<br>"
    "• <b>Study Session</b> — Phiên học từng bước<br>"
    "• <b>Progress Dashboard</b> — Theo dõi tiến độ tổng thể"
    "</div></div>",
    unsafe_allow_html=True,
)
