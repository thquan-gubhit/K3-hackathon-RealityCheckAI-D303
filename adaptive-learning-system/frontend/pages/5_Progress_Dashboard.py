"""Display mastery dimensions, evidence, and unresolved misconceptions."""

from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.api_client import BackendApiError, get_progress


def _show_misconceptions(values: Any) -> None:
    if not isinstance(values, list) or not values:
        st.caption("Không có hiểu lầm nào.")
        return
    for item in values:
        if isinstance(item, dict):
            st.write(
                f"- {item.get('concept', 'Unknown')} "
                f"(count: {item.get('occurrence_count', 0)})"
            )


st.set_page_config(
    page_title="Bảng tiến độ",
    page_icon="📈",
    layout="wide",
)
st.title("📈 Bảng tiến độ")
st.write(
    "Theo dõi điểm Nhớ lại, Hiểu biết, Áp dụng, điểm thành thạo tổng thể, "
    "bằng chứng câu hỏi độc lập và các hiểu lầm còn tồn tại."
)

user_id = st.text_input("User ID", value="local-user")
if st.button("Tải tiến độ", type="primary"):
    try:
        with st.spinner("Đang tải tiến độ..."):
            st.session_state["progress_payload"] = get_progress(user_id)
    except BackendApiError as exc:
        st.error(f"Không thể tải tiến độ: {exc.message}")
        st.caption(f"Error code: {exc.code}")

payload = st.session_state.get("progress_payload")
if isinstance(payload, dict) and payload.get("user_id") == user_id:
    recommended = payload.get("recommended_next_unit_id")
    if recommended:
        st.info(f"Đơn vị Kiến thức được đề xuất tiếp theo: {recommended}")

    units = payload.get("knowledge_units", [])
    st.subheader(f"Đơn vị Kiến thức ({len(units)})")
    if not units:
        st.info("Chưa có Đơn vị Kiến thức nào được xử lý.")
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
                "Nhớ lại",
                f"{float(mastery.get('recall_score', 0)):.0%}",
            )
            columns[1].metric(
                "Hiểu biết",
                f"{float(mastery.get('understanding_score', 0)):.0%}",
            )
            columns[2].metric(
                "Áp dụng",
                f"{float(mastery.get('application_score', 0)):.0%}",
            )
            columns[3].metric(
                "Thành thạo",
                f"{float(mastery.get('mastery_score', 0)):.0%}",
            )
            st.write(f"**Trạng thái:** {mastery.get('status', 'chưa bắt đầu')}")
            st.write(
                "**Câu hỏi độc lập:** "
                f"{mastery.get('question_evidence_count', 0)}"
            )
            st.write(
                "**Câu hỏi đã trả lời:** "
                f"{item.get('answered_questions', 0)}"
            )
            st.markdown("**Hiểu lầm còn tồn tại**")
            _show_misconceptions(item.get("active_misconceptions"))
