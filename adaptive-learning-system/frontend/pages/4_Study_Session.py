"""Read, recall, receive rubric feedback, and continue adaptively."""

from __future__ import annotations

from typing import Any

import streamlit as st

from frontend.api_client import (
    BackendApiError,
    create_learning_session,
    finish_unit,
    get_knowledge_map,
    get_next_question,
    list_documents,
    run_tutor_agent,
    submit_answer,
)


def _id(item: dict[str, Any]) -> str:
    value = item.get("id")
    return str(value) if value is not None else ""


def _show_error(action: str, error: BackendApiError) -> None:
    st.error(f"{action}: {error.message}")
    st.caption(f"Error code: {error.code}")


def _show_list(label: str, values: Any) -> None:
    st.markdown(f"**{label}**")
    if isinstance(values, list) and values:
        for value in values:
            st.write(f"- {value}")
    else:
        st.caption("Không có.")


def _load_next(session_id: str) -> None:
    try:
        with st.spinner("Đang chọn hoạt động tiếp theo..."):
            st.session_state["study_next"] = get_next_question(session_id)
    except BackendApiError as exc:
        _show_error("Không thể chọn hoạt động tiếp theo", exc)


st.set_page_config(page_title="Phiên học", page_icon="🧠", layout="wide")
st.title("🧠 Phiên học")
st.write(
    "Đọc một Đơn vị Kiến thức, ẩn nó đi, trả lời từ trí nhớ, sau đó nhận "
    "phản hồi dựa trên barem và cập nhật điểm thành thạo."
)

try:
    ready_documents = [
        document
        for document in list_documents()
        if document.get("status") == "ready"
    ]
except BackendApiError as exc:
    ready_documents = []
    _show_error("Could not load documents", exc)

if not ready_documents:
    st.info("Hãy xử lý một file PDF trước khi bắt đầu phiên học.")
else:
    documents = {_id(document): document for document in ready_documents}
    document_id = st.selectbox(
        "Tài liệu",
        options=list(documents),
        format_func=lambda key: documents[key].get("filename", key),
    )
    try:
        knowledge_map = get_knowledge_map(document_id)
        units = knowledge_map.get("knowledge_units", [])
    except BackendApiError as exc:
        units = []
        _show_error("Could not load Knowledge Map", exc)

    if units:
        units_by_id = {_id(unit): unit for unit in units}
        unit_id = st.selectbox(
            "Đơn vị Kiến thức",
            options=list(units_by_id),
            format_func=lambda key: units_by_id[key].get("title", key),
        )
        unit = units_by_id[unit_id]

        if st.button("Bắt đầu phiên học", type="primary"):
            try:
                with st.spinner("Đang chuẩn bị câu hỏi..."):
                    learning_session = create_learning_session(
                        document_id,
                        unit_id,
                    )
            except BackendApiError as exc:
                _show_error("Could not start session", exc)
            else:
                st.session_state["study_session"] = learning_session
                st.session_state["study_unit_id"] = unit_id
                st.session_state["study_read_done"] = False
                st.session_state.pop("study_next", None)
                st.session_state.pop("study_result", None)

        active = st.session_state.get("study_session")
        if (
            isinstance(active, dict)
            and st.session_state.get("study_unit_id") == unit_id
        ):
            session_id = _id(active)
            st.caption(f"Session: {session_id}")

            if not st.session_state.get("study_read_done", False):
                st.subheader(unit.get("title", "Knowledge Unit"))
                st.write(unit.get("summary", ""))
                left, right = st.columns(2)
                with left:
                    _show_list(
                        "Learning objectives",
                        unit.get("learning_objectives"),
                    )
                    _show_list("Key concepts", unit.get("key_concepts"))
                with right:
                    _show_list(
                        "Common misconceptions",
                        unit.get("common_misconceptions"),
                    )
                    _show_list("Prerequisites", unit.get("prerequisites"))
                if st.button("Tôi đã đọc xong — ẩn đơn vị kiến thức"):
                    st.session_state["study_read_done"] = True
                    _load_next(session_id)
                    st.rerun()
            else:
                st.info(
                    "Đơn vị kiến thức đã được ẩn. Hãy tự nhớ lại và trả lời."
                )
                if "study_next" not in st.session_state:
                    if st.button("Tải câu hỏi tiếp theo", type="primary"):
                        _load_next(session_id)

                next_activity = st.session_state.get("study_next")
                if isinstance(next_activity, dict):
                    question = next_activity.get("question")
                    st.caption(
                        f"Next action: {next_activity.get('next_action', '—')}"
                    )
                    st.caption(next_activity.get("route_reason", ""))
                    if isinstance(question, dict):
                        st.subheader(
                            f"Câu hỏi {str(question.get('question_type', '')).title()}"
                        )
                        st.write(question.get("question_text", ""))
                        answer = st.text_area(
                            "Câu trả lời của bạn",
                            key=f"answer_{question.get('id')}",
                            height=160,
                            placeholder=(
                                "Gõ câu trả lời từ trí nhớ...\n"
                                "(Mẹo: Có thể dùng ký tự thường thay cho ký hiệu Toán học: u thay cho ∪, n thay cho ∩, <= thay cho ≤...)"
                            ),
                        )
                        if st.button(
                            "Gửi câu trả lời",
                            type="primary",
                            disabled=not answer.strip(),
                        ):
                            try:
                                with st.spinner(
                                    "Đang chấm điểm theo barem..."
                                ):
                                    result = submit_answer(
                                        session_id,
                                        str(question["id"]),
                                        answer,
                                    )
                            except BackendApiError as exc:
                                _show_error("Evaluation failed", exc)
                            else:
                                st.session_state["study_result"] = result
                                if result.get("next_action") != "ASK_CLARIFICATION":
                                    st.session_state.pop("study_next", None)
                                st.rerun()
                    elif next_activity.get("next_action") == "ACTIVATE_TUTOR_AGENT":
                        if st.button("Chạy Gia sư AI", type="primary"):
                            try:
                                result = run_tutor_agent(
                                    session_id,
                                    reason="REPEATED_MISCONCEPTION",
                                )
                            except BackendApiError as exc:
                                _show_error("Tutor Agent could not run", exc)
                            else:
                                st.session_state["agent_result"] = result
                    else:
                        st.info("Không còn câu hỏi ở thời điểm này.")

                result = st.session_state.get("study_result")
                if isinstance(result, dict):
                    evaluation = result.get("evaluation", {})
                    mastery = result.get("mastery", {})
                    st.subheader("Phản hồi")
                    first, second = st.columns(2)
                    with first:
                        _show_list(
                            "Ý đúng",
                            evaluation.get("correct_points"),
                        )
                        _show_list(
                            "Ý còn thiếu",
                            evaluation.get("missing_points"),
                        )
                    with second:
                        _show_list(
                            "Ý chưa đúng",
                            evaluation.get("incorrect_points"),
                        )
                        _show_list(
                            "Hiểu lầm được phát hiện",
                            evaluation.get("detected_misconceptions"),
                        )
                    st.write(evaluation.get("feedback", ""))
                    st.metric(
                        "Mastery",
                        f"{float(mastery.get('mastery_score', 0)):.0%}",
                    )
                    next_action = result.get('next_action', 'CONTINUE')
                    st.caption(
                        f"Next action: {next_action}"
                    )
                    if next_action == "ASK_CLARIFICATION":
                        st.info("Hãy đọc phản hồi ở trên và thử giải thích chi tiết hơn nhé!")
                        if st.button("Trả lời lại"):
                            st.session_state.pop("study_result", None)
                            st.rerun()
                    else:
                        if st.button("Tiếp tục"):
                            st.session_state.pop("study_result", None)
                            _load_next(session_id)
                            st.rerun()

                agent_result = st.session_state.get("agent_result")
                if isinstance(agent_result, dict):
                    st.subheader("Gia sư AI")
                    st.caption(
                        f"Status: {agent_result.get('status')} · "
                        f"Steps: {len(agent_result.get('steps', []))}"
                    )
                    for step in agent_result.get("steps", []):
                        with st.expander(
                            f"Step {step.get('step_number')} — "
                            f"{step.get('action')}"
                        ):
                            st.write(step.get("observation", {}))

                if st.button("Hoàn thành đơn vị kiến thức"):
                    try:
                        finished = finish_unit(session_id)
                    except BackendApiError as exc:
                        _show_error("Unit cannot be finished yet", exc)
                    else:
                        st.success(f"Session status: {finished.get('status')}")
    else:
        st.info("Tài liệu được chọn không có Đơn vị Kiến thức nào.")
