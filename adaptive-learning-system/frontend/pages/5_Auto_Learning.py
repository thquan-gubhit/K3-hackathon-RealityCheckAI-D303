"""One-upload flow from PDF to Knowledge Map and adaptive study."""

from __future__ import annotations

import hashlib
from typing import Any

import fitz
import streamlit as st

from frontend.api_client import (
    BackendApiError,
    create_learning_session,
    get_next_question,
    process_document,
    submit_answer,
    upload_document,
)


DOCUMENT_STATE_KEYS = (
    "auto_file_hash",
    "auto_pdf_bytes",
    "auto_document",
    "auto_processing_result",
    "auto_active_unit_id",
    "auto_session",
    "auto_next",
    "auto_result",
    "auto_error",
)


def _id(item: dict[str, Any]) -> str:
    value = item.get("id")
    return str(value) if value is not None else ""


def _reset_document_state() -> None:
    for key in DOCUMENT_STATE_KEYS:
        st.session_state.pop(key, None)


def _show_list(label: str, values: Any) -> None:
    st.markdown(f"**{label}**")
    if isinstance(values, list) and values:
        for value in values:
            st.write(f"- {value}")
    else:
        st.caption("Không có.")


def _slide_range(pages: Any) -> str:
    if not isinstance(pages, list) or not pages:
        return "Không có slide nguồn"
    normalized = sorted({int(page) for page in pages})
    ranges: list[str] = []
    start = previous = normalized[0]
    for page in normalized[1:]:
        if page == previous + 1:
            previous = page
            continue
        ranges.append(str(start) if start == previous else f"{start}–{previous}")
        start = previous = page
    ranges.append(str(start) if start == previous else f"{start}–{previous}")
    return "Slides " + ", ".join(ranges)


@st.cache_data(show_spinner=False)
def _render_slide(
    pdf_bytes: bytes,
    file_hash: str,
    page_number: int,
) -> bytes:
    """Render one one-based PDF page; file_hash keeps the cache source-safe."""

    del file_hash
    with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
        if page_number < 1 or page_number > document.page_count:
            raise ValueError("Slide number is outside the uploaded PDF.")
        page = document.load_page(page_number - 1)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(1.45, 1.45), alpha=False)
        return pixmap.tobytes("png")


def _remember_error(stage: str, error: BackendApiError) -> None:
    st.session_state["auto_error"] = {
        "stage": stage,
        "message": error.message,
        "code": error.code,
    }


def _ensure_document_pipeline(
    *,
    filename: str,
    content: bytes,
    content_type: str,
) -> None:
    if "auto_document" not in st.session_state:
        with st.spinner("1/3 Đang upload PDF..."):
            st.session_state["auto_document"] = upload_document(
                filename,
                content,
                content_type=content_type,
            )
    if "auto_processing_result" not in st.session_state:
        document_id = _id(st.session_state["auto_document"])
        with st.spinner(
            "2/3 Đang đọc slide và tự động tạo Knowledge Map..."
        ):
            st.session_state["auto_processing_result"] = process_document(
                document_id
            )


def _ensure_study_session(document_id: str, unit_id: str) -> None:
    if st.session_state.get("auto_active_unit_id") != unit_id:
        st.session_state["auto_active_unit_id"] = unit_id
        st.session_state.pop("auto_session", None)
        st.session_state.pop("auto_next", None)
        st.session_state.pop("auto_result", None)

    if "auto_session" not in st.session_state:
        with st.spinner(
            "3/3 Đang tạo lesson và câu hỏi đầu tiên..."
        ):
            st.session_state["auto_session"] = create_learning_session(
                document_id,
                unit_id,
            )
    if "auto_next" not in st.session_state:
        session_id = _id(st.session_state["auto_session"])
        st.session_state["auto_next"] = get_next_question(session_id)


def _show_feedback(result: dict[str, Any]) -> None:
    evaluation = result.get("evaluation", {})
    mastery = result.get("mastery", {})
    st.subheader("Kết quả câu trả lời trước")
    first, second = st.columns(2)
    with first:
        _show_list("Ý đúng", evaluation.get("correct_points"))
        _show_list("Ý còn thiếu", evaluation.get("missing_points"))
    with second:
        _show_list("Ý chưa đúng", evaluation.get("incorrect_points"))
        _show_list(
            "Hiểu lầm được phát hiện",
            evaluation.get("detected_misconceptions"),
        )
    if evaluation.get("feedback"):
        st.info(str(evaluation["feedback"]))
    st.metric(
        "Mastery",
        f"{float(mastery.get('mastery_score', 0)):.0%}",
    )


st.set_page_config(
    page_title="Auto Learning",
    page_icon="⚡",
    layout="wide",
)
st.title("Auto Learning — Upload một lần")
st.write(
    "Chọn một PDF có text. Hệ thống tự upload, tạo Knowledge Map, tạo lesson "
    "và nạp câu hỏi đầu tiên; không cần chuyển tab hay bấm thêm."
)

uploaded_file = st.file_uploader(
    "Chọn slide PDF",
    type=["pdf"],
    accept_multiple_files=False,
    help="Sau khi chọn file, pipeline tự động bắt đầu.",
    key="auto_pdf_input",
)

if uploaded_file is not None:
    current_bytes = uploaded_file.getvalue()
    current_hash = hashlib.sha256(current_bytes).hexdigest()
    if st.session_state.get("auto_file_hash") != current_hash:
        _reset_document_state()
        st.session_state["auto_file_hash"] = current_hash
        st.session_state["auto_pdf_bytes"] = current_bytes

    if "auto_error" not in st.session_state:
        try:
            _ensure_document_pipeline(
                filename=uploaded_file.name,
                content=current_bytes,
                content_type=uploaded_file.type or "application/pdf",
            )
        except BackendApiError as exc:
            stage = (
                "process"
                if "auto_document" in st.session_state
                else "upload"
            )
            _remember_error(stage, exc)

pdf_bytes = st.session_state.get("auto_pdf_bytes")
processing_result = st.session_state.get("auto_processing_result")
pipeline_error = st.session_state.get("auto_error")

if isinstance(pipeline_error, dict):
    st.error(
        f"Pipeline dừng tại bước {pipeline_error.get('stage')}: "
        f"{pipeline_error.get('message')}"
    )
    st.caption(f"Error code: {pipeline_error.get('code')}")
    if st.button("Thử lại bước bị lỗi", type="primary"):
        stage = pipeline_error.get("stage")
        st.session_state.pop("auto_error", None)
        if stage == "upload":
            st.session_state.pop("auto_document", None)
            st.session_state.pop("auto_processing_result", None)
        elif stage == "process":
            st.session_state.pop("auto_processing_result", None)
        elif stage == "study":
            st.session_state.pop("auto_session", None)
            st.session_state.pop("auto_next", None)
        st.rerun()
elif uploaded_file is None and not isinstance(processing_result, dict):
    st.info("Chọn một PDF để bắt đầu luồng học tự động.")

if (
    isinstance(processing_result, dict)
    and isinstance(pdf_bytes, bytes)
    and not isinstance(pipeline_error, dict)
):
    document = processing_result.get("document", {})
    units = processing_result.get("knowledge_units", [])
    coverage = processing_result.get("coverage", {})
    document_id = _id(document)

    st.success(
        "Đã tạo xong Knowledge Map và lesson tự động."
    )
    metrics = st.columns(4)
    metrics[0].metric("Knowledge Units", len(units))
    metrics[1].metric("Slides", document.get("page_count", "—"))
    metrics[2].metric("Slides được phủ", coverage.get("covered_pages", "—"))
    ratio = coverage.get("coverage_ratio")
    metrics[3].metric(
        "Coverage",
        f"{ratio:.0%}" if isinstance(ratio, (int, float)) else "—",
    )

    st.subheader("Knowledge Map")
    for position, item in enumerate(units, start=1):
        st.write(
            f"**KU{position}: {item.get('title', 'Untitled')}** · "
            f"{_slide_range(item.get('source_pages'))}"
        )

    if units:
        units_by_id = {_id(item): item for item in units}
        selected_unit_id = st.selectbox(
            "Knowledge Unit đang học",
            options=list(units_by_id),
            format_func=lambda unit_id: (
                f"{units_by_id[unit_id].get('title', unit_id)} · "
                f"{_slide_range(units_by_id[unit_id].get('source_pages'))}"
            ),
            key=f"auto_unit_{st.session_state['auto_file_hash']}",
        )
        selected_unit = units_by_id[selected_unit_id]

        try:
            _ensure_study_session(document_id, selected_unit_id)
        except BackendApiError as exc:
            _remember_error("study", exc)
            st.error(f"Không thể tạo lesson: {exc.message}")
            st.caption(f"Error code: {exc.code}")
        else:
            st.divider()
            slide_column, lesson_column = st.columns([1.15, 1])

            source_pages = selected_unit.get("source_pages", [])
            with slide_column:
                st.subheader(
                    f"Slide nguồn · {_slide_range(source_pages)}"
                )
                for source_page in source_pages:
                    try:
                        slide_png = _render_slide(
                            pdf_bytes,
                            st.session_state["auto_file_hash"],
                            int(source_page),
                        )
                    except (RuntimeError, ValueError) as exc:
                        st.error(
                            f"Không thể hiển thị slide {source_page}: {exc}"
                        )
                    else:
                        st.image(
                            slide_png,
                            caption=(
                                f"Slide {source_page} / "
                                f"{document.get('page_count', '—')}"
                            ),
                            use_container_width=True,
                        )

            with lesson_column:
                st.subheader(selected_unit.get("title", "Knowledge Unit"))
                st.write(selected_unit.get("summary", ""))
                _show_list(
                    "Mục tiêu học tập",
                    selected_unit.get("learning_objectives"),
                )
                _show_list(
                    "Khái niệm chính",
                    selected_unit.get("key_concepts"),
                )
                _show_list(
                    "Hiểu lầm thường gặp",
                    selected_unit.get("common_misconceptions"),
                )
                st.caption(
                    "Nguồn: "
                    + _slide_range(selected_unit.get("source_pages"))
                )

            result = st.session_state.get("auto_result")
            if isinstance(result, dict):
                _show_feedback(result)

            next_activity = st.session_state.get("auto_next")
            if isinstance(next_activity, dict):
                question = next_activity.get("question")
                st.subheader("Câu hỏi tiếp theo")
                st.caption(
                    f"Loại: {next_activity.get('next_action', '—')} · "
                    f"{next_activity.get('route_reason', '')}"
                )
                if isinstance(question, dict):
                    st.write(question.get("question_text", ""))
                    question_id = str(question.get("id", ""))
                    with st.form(f"auto_answer_form_{question_id}"):
                        answer = st.text_area(
                            "Câu trả lời của bạn",
                            height=150,
                        )
                        submitted = st.form_submit_button(
                            "Gửi câu trả lời",
                            type="primary",
                            disabled=not answer.strip(),
                        )
                    if submitted:
                        session_id = _id(
                            st.session_state["auto_session"]
                        )
                        try:
                            with st.spinner(
                                "Đang chấm theo rubric và chọn câu tiếp..."
                            ):
                                st.session_state["auto_result"] = (
                                    submit_answer(
                                        session_id,
                                        question_id,
                                        answer,
                                    )
                                )
                                st.session_state.pop("auto_next", None)
                                st.session_state["auto_next"] = (
                                    get_next_question(session_id)
                                )
                        except BackendApiError as exc:
                            _remember_error("answer", exc)
                            st.error(f"Không thể chấm câu trả lời: {exc.message}")
                        else:
                            st.rerun()
                else:
                    st.info(
                        "Không còn câu hỏi thường ở thời điểm hiện tại. "
                        "Bạn có thể đổi Knowledge Unit để tiếp tục."
                    )
