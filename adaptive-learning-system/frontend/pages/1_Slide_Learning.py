"""Slide-centric adaptive learning — upload once, read, recall, master."""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
from typing import Any

import fitz
import streamlit as st

from frontend.api_client import (
    BackendApiError,
    create_learning_session,
    get_next_question,
    get_progress,
    process_document,
    run_tutor_agent,
    submit_answer,
    upload_document,
)

# ── Constants ────────────────────────────────────────────────────
_CSS_PATH = Path(__file__).resolve().parents[1] / "style.css"

DOCUMENT_STATE_KEYS = (
    "sl_file_hash",
    "sl_pdf_bytes",
    "sl_document",
    "sl_processing_result",
    "sl_active_unit_id",
    "sl_session",
    "sl_next",
    "sl_result",
    "sl_error",
    "sl_phase",
    "sl_peek_count",
)


# ── Helpers ──────────────────────────────────────────────────────
def _id(item: dict[str, Any]) -> str:
    value = item.get("id")
    return str(value) if value is not None else ""


def _reset_state() -> None:
    for key in DOCUMENT_STATE_KEYS:
        st.session_state.pop(key, None)


def _inject_css() -> None:
    """Load and inject custom CSS once per session."""
    if _CSS_PATH.exists():
        css = _CSS_PATH.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _slide_range(pages: Any) -> str:
    if not isinstance(pages, list) or not pages:
        return "Không có slide nguồn"
    normalized = sorted({int(p) for p in pages})
    ranges: list[str] = []
    start = prev = normalized[0]
    for p in normalized[1:]:
        if p == prev + 1:
            prev = p
            continue
        ranges.append(str(start) if start == prev else f"{start}–{prev}")
        start = prev = p
    ranges.append(str(start) if start == prev else f"{start}–{prev}")
    return "Slides " + ", ".join(ranges)


@st.cache_data(show_spinner=False)
def _render_slide(pdf_bytes: bytes, file_hash: str, page_number: int) -> bytes:
    del file_hash
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        if page_number < 1 or page_number > doc.page_count:
            raise ValueError("Slide number is outside the uploaded PDF.")
        page = doc.load_page(page_number - 1)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(1.45, 1.45), alpha=False)
        return pixmap.tobytes("png")


def _remember_error(stage: str, error: BackendApiError) -> None:
    st.session_state["sl_error"] = {
        "stage": stage,
        "message": error.message,
        "code": error.code,
    }


# ── Pipeline helpers ─────────────────────────────────────────────
def _ensure_document_pipeline(
    *, filename: str, content: bytes, content_type: str
) -> None:
    if "sl_document" not in st.session_state:
        with st.spinner("⏳ 1/3 — Đang upload PDF…"):
            st.session_state["sl_document"] = upload_document(
                filename, content, content_type=content_type
            )
    if "sl_processing_result" not in st.session_state:
        doc_id = _id(st.session_state["sl_document"])
        with st.spinner("⏳ 2/3 — Đang đọc slide & tạo Knowledge Map…"):
            st.session_state["sl_processing_result"] = process_document(doc_id)


def _ensure_study_session(document_id: str, unit_id: str) -> None:
    if st.session_state.get("sl_active_unit_id") != unit_id:
        st.session_state["sl_active_unit_id"] = unit_id
        st.session_state.pop("sl_session", None)
        st.session_state.pop("sl_next", None)
        st.session_state.pop("sl_result", None)
        st.session_state["sl_phase"] = "reading"
        st.session_state["sl_peek_count"] = 0

    if "sl_session" not in st.session_state:
        with st.spinner("⏳ 3/3 — Đang tạo bài học & câu hỏi…"):
            st.session_state["sl_session"] = create_learning_session(
                document_id, unit_id
            )
    if "sl_next" not in st.session_state:
        session_id = _id(st.session_state["sl_session"])
        st.session_state["sl_next"] = get_next_question(session_id)


# ── SVG Radar Chart ──────────────────────────────────────────────
def _build_radar_svg(scores: dict[str, float]) -> str:
    """Generate a radar chart as inline SVG for 4 dimensions."""
    labels = ["Correctness", "Coverage", "Reasoning", "Application"]
    keys = ["correctness", "coverage", "reasoning", "application"]
    values = [float(scores.get(k, 0)) for k in keys]

    cx, cy, r = 140, 140, 100
    n = len(labels)
    angles = [(-math.pi / 2) + (2 * math.pi * i / n) for i in range(n)]

    # Grid rings
    grid_lines = ""
    for level in [0.25, 0.5, 0.75, 1.0]:
        pts = " ".join(
            f"{cx + r * level * math.cos(a):.1f},{cy + r * level * math.sin(a):.1f}"
            for a in angles
        )
        grid_lines += f'<polygon points="{pts}" class="radar-grid"/>\n'

    # Axis lines
    axis_lines = ""
    for a in angles:
        x2 = cx + r * math.cos(a)
        y2 = cy + r * math.sin(a)
        axis_lines += (
            f'<line x1="{cx}" y1="{cy}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'class="radar-axis"/>\n'
        )

    # Data polygon
    data_pts = []
    dot_circles = ""
    for i, v in enumerate(values):
        x = cx + r * v * math.cos(angles[i])
        y = cy + r * v * math.sin(angles[i])
        data_pts.append(f"{x:.1f},{y:.1f}")
        dot_circles += (
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" class="radar-point"/>\n'
        )
    data_polygon = f'<polygon points="{" ".join(data_pts)}" class="radar-area"/>\n'

    # Labels
    label_offset = 22
    label_elems = ""
    for i, label in enumerate(labels):
        lx = cx + (r + label_offset) * math.cos(angles[i])
        ly = cy + (r + label_offset) * math.sin(angles[i])
        pct = f"{values[i]:.0%}"
        label_elems += (
            f'<text x="{lx:.1f}" y="{ly:.1f}" class="radar-label">'
            f"{label}\n"
            f'<tspan x="{lx:.1f}" dy="14" style="font-weight:700;'
            f'fill:#7c5cfc">{pct}</tspan></text>\n'
        )

    return (
        '<div class="radar-container">'
        f'<svg viewBox="0 0 280 280" xmlns="http://www.w3.org/2000/svg">'
        f"{grid_lines}{axis_lines}{data_polygon}{dot_circles}{label_elems}"
        "</svg></div>"
    )


# ── Feedback Renderer ────────────────────────────────────────────
def _render_feedback_card(
    category: str, label: str, items: list[str] | None
) -> str:
    if not items:
        return ""
    html_items = "".join(
        f'<div class="feedback-text">• {item}</div>' for item in items
    )
    return (
        f'<div class="feedback-{category}">'
        f'<div class="feedback-label">{label}</div>'
        f"{html_items}</div>"
    )


def _render_feedback(result: dict[str, Any]) -> None:
    evaluation = result.get("evaluation", {})
    mastery = result.get("mastery", {})

    # Radar chart
    dims = evaluation.get("dimension_scores", {})
    scores = {
        "correctness": float(dims.get("correctness", 0)),
        "coverage": float(dims.get("coverage", 0)),
        "reasoning": float(dims.get("reasoning", 0)),
        "application": float(dims.get("application", 0)),
    }
    st.markdown(_build_radar_svg(scores), unsafe_allow_html=True)

    # Feedback cards
    cards_html = ""
    cards_html += _render_feedback_card(
        "correct", "✅ Ý đúng", evaluation.get("correct_points")
    )
    cards_html += _render_feedback_card(
        "missing", "⚠️ Ý còn thiếu", evaluation.get("missing_points")
    )
    cards_html += _render_feedback_card(
        "misconception",
        "🛑 Hiểu lầm nghiêm trọng",
        evaluation.get("detected_misconceptions"),
    )
    cards_html += _render_feedback_card(
        "missing", "❌ Ý chưa đúng", evaluation.get("incorrect_points")
    )
    if cards_html:
        st.markdown(
            f'<div class="glass-card">{cards_html}</div>',
            unsafe_allow_html=True,
        )

    # Overall feedback text
    if evaluation.get("feedback"):
        st.info(str(evaluation["feedback"]))

    # Mastery bar
    mastery_score = float(mastery.get("mastery_score", 0))
    mastery_pct = int(mastery_score * 100)
    st.markdown(
        f'<div class="glass-card">'
        f'<div class="section-header">Mastery — {mastery_pct}%</div>'
        f'<div class="mastery-bar-container">'
        f'<div class="mastery-bar-fill" style="width:{mastery_pct}%"></div>'
        f"</div></div>",
        unsafe_allow_html=True,
    )


# ── Sidebar Progress Tree ────────────────────────────────────────
def _render_sidebar_progress(
    units: list[dict[str, Any]], active_unit_id: str | None
) -> None:
    with st.sidebar:
        st.markdown("### 🌐 Cài đặt / Settings")
        selected_lang = st.selectbox(
            "Ngôn ngữ LLM / LLM Language",
            options=["Tiếng Việt", "English"],
            index=0 if st.session_state.get("ui_language", "Tiếng Việt") == "Tiếng Việt" else 1,
            key="ui_language",
            help="Thay đổi ngôn ngữ này sẽ áp dụng cho các tài liệu và câu hỏi ĐƯỢC TẠO MỚI sau khi đổi."
        )

        st.divider()
        st.markdown("### 📚 Tiến độ học tập")

        # Fetch progress if available
        progress_data: dict[str, Any] = {}
        try:
            progress = get_progress("local-user")
            for ku in progress.get("knowledge_units", []):
                ku_id = str(ku.get("knowledge_unit_id", ku.get("id", "")))
                progress_data[ku_id] = ku
        except BackendApiError:
            pass

        mastered_count = 0
        total_count = len(units)

        items_html = ""
        for pos, unit in enumerate(units, start=1):
            uid = _id(unit)
            title = unit.get("title", f"KU {pos}")
            ku_progress = progress_data.get(uid, {})
            ku_mastery = ku_progress.get("mastery", {})
            score = float(ku_mastery.get("mastery_score", 0))
            has_misconception = bool(ku_progress.get("active_misconceptions"))
            status_class = "not-started"
            if has_misconception:
                status_class = "misconception"
            elif score >= 0.8:
                status_class = "mastered"
                mastered_count += 1
            elif score > 0:
                status_class = "in-progress"

            active_class = " active" if uid == active_unit_id else ""
            items_html += (
                f'<div class="ku-tree-item{active_class}">'
                f'<span class="ku-status-dot {status_class}"></span>'
                f'<span style="flex:1;overflow:hidden;text-overflow:ellipsis;'
                f'white-space:nowrap">{pos}. {title}</span>'
                f"</div>"
            )

        # Progress header
        st.markdown(
            f'<div class="progress-header">'
            f'<div class="progress-fraction">{mastered_count}/{total_count}</div>'
            f'<div class="progress-label">Knowledge Units Mastered</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

        # Overall bar
        pct = int(mastered_count / total_count * 100) if total_count else 0
        st.markdown(
            f'<div class="mastery-bar-container">'
            f'<div class="mastery-bar-fill" style="width:{pct}%"></div>'
            f"</div>",
            unsafe_allow_html=True,
        )

        # Tree
        st.markdown(items_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# PAGE CONFIG & LAYOUT
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Slide Learning — Adaptive Learning System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
_inject_css()

# ── Phase badge helper ────────────────────────────────────────────
def _phase_badge(phase: str) -> str:
    labels = {
        "reading": ("📖 Đọc Slide", "reading"),
        "recall": ("🧠 Retrieval Practice", "recall"),
        "evaluated": ("📊 Đánh giá", "evaluated"),
        "tutor": ("🎓 Gia sư AI", "tutor"),
    }
    text, cls = labels.get(phase, ("❓ Unknown", "reading"))
    return f'<span class="phase-badge {cls}">{text}</span>'


# ── Main Title ────────────────────────────────────────────────────
st.markdown(
    '<h1 style="font-family:Inter,sans-serif;'
    "background:linear-gradient(135deg,#7c5cfc 0%,#5ce1e6 100%);"
    "-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
    'background-clip:text">🎓 Slide Learning</h1>',
    unsafe_allow_html=True,
)
st.caption(
    "Upload một slide PDF → Đọc → Che slide → Tự kiểm tra kiến thức → "
    "Nhận đánh giá AI đa chiều → Master từng Knowledge Unit."
)

# ── Upload ────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Chọn slide PDF",
    type=["pdf"],
    accept_multiple_files=False,
    help="Sau khi chọn file, pipeline tự động bắt đầu.",
    key="sl_pdf_input",
)

if uploaded_file is not None:
    current_bytes = uploaded_file.getvalue()
    current_hash = hashlib.sha256(current_bytes).hexdigest()
    if st.session_state.get("sl_file_hash") != current_hash:
        _reset_state()
        st.session_state["sl_file_hash"] = current_hash
        st.session_state["sl_pdf_bytes"] = current_bytes

    if "sl_error" not in st.session_state:
        try:
            _ensure_document_pipeline(
                filename=uploaded_file.name,
                content=current_bytes,
                content_type=uploaded_file.type or "application/pdf",
            )
        except BackendApiError as exc:
            stage = (
                "process" if "sl_document" in st.session_state else "upload"
            )
            _remember_error(stage, exc)

# ── Error handling ────────────────────────────────────────────────
pdf_bytes = st.session_state.get("sl_pdf_bytes")
processing_result = st.session_state.get("sl_processing_result")
pipeline_error = st.session_state.get("sl_error")

if isinstance(pipeline_error, dict):
    st.error(
        f"Pipeline dừng tại bước **{pipeline_error.get('stage')}**: "
        f"{pipeline_error.get('message')}"
    )
    st.caption(f"Error code: {pipeline_error.get('code')}")
    if st.button("🔄 Thử lại bước bị lỗi", type="primary"):
        stage = pipeline_error.get("stage")
        st.session_state.pop("sl_error", None)
        if stage == "upload":
            st.session_state.pop("sl_document", None)
            st.session_state.pop("sl_processing_result", None)
        elif stage == "process":
            st.session_state.pop("sl_processing_result", None)
        elif stage == "study":
            st.session_state.pop("sl_session", None)
            st.session_state.pop("sl_next", None)
        st.rerun()
elif uploaded_file is None and not isinstance(processing_result, dict):
    st.info("👆 Chọn một file PDF slide để bắt đầu luồng học tập.")

# ══════════════════════════════════════════════════════════════════
# MAIN WORKSPACE
# ══════════════════════════════════════════════════════════════════
if (
    isinstance(processing_result, dict)
    and isinstance(pdf_bytes, bytes)
    and not isinstance(pipeline_error, dict)
):
    document = processing_result.get("document", {})
    units = processing_result.get("knowledge_units", [])
    coverage = processing_result.get("coverage", {})
    document_id = _id(document)

    # ── Knowledge Map summary ────────────────────────────────────
    st.success("✅ Đã tạo xong Knowledge Map!")
    mc = st.columns(4)
    mc[0].metric("Knowledge Units", len(units))
    mc[1].metric("Tổng slides", document.get("page_count", "—"))
    mc[2].metric("Slides được phủ", coverage.get("covered_pages", "—"))
    ratio = coverage.get("coverage_ratio")
    mc[3].metric(
        "Coverage",
        f"{ratio:.0%}" if isinstance(ratio, (int, float)) else "—",
    )

    if not units:
        st.warning("Không tìm thấy Knowledge Unit nào trong PDF này.")
    else:
        # ── Unit selector ────────────────────────────────────────
        units_by_id = {_id(u): u for u in units}
        selected_unit_id = st.selectbox(
            "📘 Chọn Knowledge Unit để học",
            options=list(units_by_id),
            format_func=lambda uid: (
                f"{units_by_id[uid].get('title', uid)} · "
                f"{_slide_range(units_by_id[uid].get('source_pages'))}"
            ),
            key=f"sl_unit_{st.session_state['sl_file_hash']}",
        )
        selected_unit = units_by_id[selected_unit_id]

        # ── Ensure study session ─────────────────────────────────
        try:
            _ensure_study_session(document_id, selected_unit_id)
        except BackendApiError as exc:
            _remember_error("study", exc)
            st.error(f"Không thể tạo bài học: {exc.message}")
        else:
            # ── Sidebar progress tree ────────────────────────────
            _render_sidebar_progress(units, selected_unit_id)

            # ── Phase state ──────────────────────────────────────
            phase = st.session_state.get("sl_phase", "reading")
            peek_count = st.session_state.get("sl_peek_count", 0)

            # Check if tutor agent should be activated
            next_activity = st.session_state.get("sl_next")
            if (
                isinstance(next_activity, dict)
                and next_activity.get("next_action") == "ACTIVATE_TUTOR_AGENT"
                and phase != "tutor"
            ):
                st.session_state["sl_phase"] = "tutor"
                phase = "tutor"

            st.divider()
            st.markdown(_phase_badge(phase), unsafe_allow_html=True)

            # ── SPLIT VIEW ───────────────────────────────────────
            slide_col, lesson_col = st.columns([1.15, 1])
            source_pages = selected_unit.get("source_pages", [])

            # ─── LEFT: SLIDE VIEWER ──────────────────────────────
            with slide_col:
                st.markdown(
                    f'<div class="section-header">'
                    f"📑 Slide nguồn · {_slide_range(source_pages)}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                is_blurred = phase in ("recall", "evaluated", "tutor")

                if is_blurred:
                    # Blurred slides with overlay
                    st.markdown(
                        '<div class="slide-blur-overlay">',
                        unsafe_allow_html=True,
                    )

                for sp in source_pages:
                    try:
                        slide_png = _render_slide(
                            pdf_bytes,
                            st.session_state["sl_file_hash"],
                            int(sp),
                        )
                    except (RuntimeError, ValueError) as exc:
                        st.error(f"Không thể hiển thị slide {sp}: {exc}")
                    else:
                        if is_blurred:
                            # Use HTML img with blur for proper CSS overlay
                            import base64

                            b64 = base64.b64encode(slide_png).decode()
                            st.markdown(
                                f'<img src="data:image/png;base64,{b64}" '
                                f'style="width:100%;border-radius:12px;'
                                f'filter:blur(18px) brightness(0.5);'
                                f'transform:scale(1.02)" />',
                                unsafe_allow_html=True,
                            )
                        else:
                            st.image(
                                slide_png,
                                caption=(
                                    f"Slide {sp} / "
                                    f"{document.get('page_count', '—')}"
                                ),
                                use_container_width=True,
                            )

                if is_blurred:
                    st.markdown(
                        '<div style="text-align:center;padding:1rem 0">'
                        '<div style="font-size:2.5rem">🔒</div>'
                        '<div style="font-family:Inter,sans-serif;'
                        "font-weight:700;font-size:1.1rem;"
                        "background:linear-gradient(135deg,#7c5cfc,#5ce1e6);"
                        "-webkit-background-clip:text;"
                        "-webkit-text-fill-color:transparent;"
                        'background-clip:text">'
                        "Slide đã bị ẩn</div>"
                        '<div style="font-family:Inter,sans-serif;'
                        "font-size:0.85rem;color:#9d9db5;"
                        'margin-top:0.25rem">'
                        "Hãy tự nhớ lại kiến thức từ slide!</div>"
                        "</div>",
                        unsafe_allow_html=True,
                    )
                    # Peek button
                    if st.button(
                        f"👁 Xem lại Slide (đã peek {peek_count} lần)",
                        key="peek_btn",
                    ):
                        st.session_state["sl_phase"] = "reading"
                        st.session_state["sl_peek_count"] = peek_count + 1
                        st.rerun()

                    if peek_count > 0:
                        st.markdown(
                            f'<div class="peek-warning">'
                            f"⚠️ Bạn đã xem lại slide {peek_count} lần. "
                            f"Cố gắng tự nhớ mà không peek nhé!"
                            f"</div>",
                            unsafe_allow_html=True,
                        )
                    st.markdown("</div>", unsafe_allow_html=True)

            # ─── RIGHT: RECALL & EVALUATION ──────────────────────
            with lesson_col:
                # ── READING phase ────────────────────────────────
                if phase == "reading":
                    st.markdown(
                        f'<div class="section-header">'
                        f"📖 {selected_unit.get('title', 'Knowledge Unit')}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                    st.write(selected_unit.get("summary", ""))

                    # Learning objectives
                    objectives = selected_unit.get("learning_objectives", [])
                    if objectives:
                        st.markdown("**🎯 Mục tiêu học tập**")
                        for obj in objectives:
                            st.write(f"- {obj}")

                    # Key concepts
                    concepts = selected_unit.get("key_concepts", [])
                    if concepts:
                        st.markdown("**💡 Khái niệm chính**")
                        for c in concepts:
                            st.write(f"- {c}")

                    # Common misconceptions
                    misconceptions = selected_unit.get(
                        "common_misconceptions", []
                    )
                    if misconceptions:
                        st.markdown("**⚠️ Hiểu lầm thường gặp**")
                        for m in misconceptions:
                            st.write(f"- {m}")

                    st.markdown("---")
                    if st.button(
                        "✅ Tôi đã sẵn sàng — Bắt đầu kiểm tra!",
                        type="primary",
                        use_container_width=True,
                        key="ready_btn",
                    ):
                        st.session_state["sl_phase"] = "recall"
                        st.rerun()

                # ── RECALL phase ─────────────────────────────────
                elif phase == "recall":
                    st.markdown(
                        f'<div class="section-header">'
                        f"🧠 Retrieval Practice"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    # Show previous result if exists
                    prev_result = st.session_state.get("sl_result")
                    if isinstance(prev_result, dict):
                        with st.expander(
                            "📊 Xem lại kết quả câu trước", expanded=False
                        ):
                            _render_feedback(prev_result)

                    next_act = st.session_state.get("sl_next")
                    if isinstance(next_act, dict):
                        question = next_act.get("question")
                        st.caption(
                            f"Loại: {next_act.get('next_action', '—')} · "
                            f"{next_act.get('route_reason', '')}"
                        )
                        if isinstance(question, dict):
                            q_type = str(
                                question.get("question_type", "")
                            ).title()
                            st.markdown(
                                f'<div class="glass-card">'
                                f'<div class="feedback-label" '
                                f'style="color:#5ce1e6">Câu hỏi {q_type}</div>'
                                f'<div class="feedback-text" '
                                f'style="font-size:1rem;margin-top:0.5rem">'
                                f"{question.get('question_text', '')}"
                                f"</div></div>",
                                unsafe_allow_html=True,
                            )

                            q_id = str(question.get("id", ""))
                            with st.form(f"answer_form_{q_id}"):
                                answer = st.text_area(
                                    "✍️ Câu trả lời của bạn",
                                    height=180,
                                    placeholder=(
                                        "Gõ câu trả lời từ trí nhớ. "
                                        "Hãy giải thích chi tiết nhất có thể…\n"
                                        "(Mẹo: Có thể dùng ký tự thường thay cho ký hiệu Toán học: u thay cho ∪, n thay cho ∩, <= thay cho ≤...)"
                                    ),
                                )
                                submitted = st.form_submit_button(
                                    "🚀 Gửi câu trả lời",
                                    type="primary",
                                    use_container_width=True,
                                )

                            if submitted and answer.strip():
                                session_id = _id(
                                    st.session_state["sl_session"]
                                )
                                try:
                                    with st.spinner(
                                        "🤖 AI đang chấm bằng Rubric…"
                                    ):
                                        st.session_state["sl_result"] = (
                                            submit_answer(
                                                session_id, q_id, answer
                                            )
                                        )
                                        st.session_state["sl_phase"] = (
                                            "evaluated"
                                        )
                                        st.session_state.pop("sl_next", None)
                                        st.session_state["sl_next"] = (
                                            get_next_question(session_id)
                                        )
                                except BackendApiError as exc:
                                    _remember_error("answer", exc)
                                    st.error(
                                        f"Không thể chấm: {exc.message}"
                                    )
                                else:
                                    st.rerun()
                        else:
                            st.info(
                                "Không còn câu hỏi ở thời điểm này. "
                                "Bạn có thể đổi Knowledge Unit."
                            )

                # ── EVALUATED phase ──────────────────────────────
                elif phase == "evaluated":
                    st.markdown(
                        f'<div class="section-header">'
                        f"📊 Kết quả đánh giá"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    result = st.session_state.get("sl_result")
                    if isinstance(result, dict):
                        _render_feedback(result)

                        st.caption(
                            f"Next action: "
                            f"{result.get('next_action', 'CONTINUE')}"
                        )

                    # Next action buttons
                    btn_cols = st.columns(2)
                    with btn_cols[0]:
                        if st.button(
                            "➡️ Câu hỏi tiếp theo",
                            type="primary",
                            use_container_width=True,
                            key="next_q_btn",
                        ):
                            st.session_state["sl_phase"] = "recall"
                            st.rerun()
                    with btn_cols[1]:
                        if st.button(
                            "📖 Đọc lại Slide",
                            use_container_width=True,
                            key="reread_btn",
                        ):
                            st.session_state["sl_phase"] = "reading"
                            st.session_state["sl_peek_count"] = (
                                st.session_state.get("sl_peek_count", 0) + 1
                            )
                            st.rerun()

                # ── TUTOR phase ──────────────────────────────────
                elif phase == "tutor":
                    st.markdown(
                        f'<div class="section-header">'
                        f"🎓 Gia sư AI — Remediation"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    st.markdown(
                        '<div class="glass-card">'
                        '<div class="feedback-misconception">'
                        '<div class="feedback-label">'
                        "🛑 Phát hiện lỗi hiểu sai nghiêm trọng"
                        "</div>"
                        '<div class="feedback-text">'
                        "Hệ thống tạm dừng bài kiểm tra. "
                        "Gia sư AI sẽ hướng dẫn bạn hiểu lại "
                        "kiến thức một cách chính xác."
                        "</div></div></div>",
                        unsafe_allow_html=True,
                    )

                    agent_result = st.session_state.get("sl_agent_result")

                    if not isinstance(agent_result, dict):
                        if st.button(
                            "🎓 Bắt đầu phiên Gia sư",
                            type="primary",
                            use_container_width=True,
                            key="tutor_btn",
                        ):
                            session_id = _id(
                                st.session_state["sl_session"]
                            )
                            try:
                                with st.spinner(
                                    "🎓 Gia sư AI đang chuẩn bị…"
                                ):
                                    st.session_state["sl_agent_result"] = (
                                        run_tutor_agent(
                                            session_id,
                                            reason="REPEATED_MISCONCEPTION",
                                        )
                                    )
                            except BackendApiError as exc:
                                st.error(
                                    f"Gia sư AI gặp lỗi: {exc.message}"
                                )
                            else:
                                st.rerun()
                    else:
                        st.caption(
                            f"Trạng thái: {agent_result.get('status')} · "
                            f"Bước: {len(agent_result.get('steps', []))}"
                        )
                        for step in agent_result.get("steps", []):
                            with st.expander(
                                f"Bước {step.get('step_number')} — "
                                f"{step.get('action')}",
                                expanded=True,
                            ):
                                obs = step.get("observation", {})
                                if isinstance(obs, dict):
                                    if obs.get("message"):
                                        st.markdown(obs["message"])
                                    if obs.get("explanation"):
                                        st.info(obs["explanation"])
                                else:
                                    st.write(obs)

                        if st.button(
                            "✅ Đã hiểu — Quay lại học tiếp",
                            type="primary",
                            use_container_width=True,
                            key="back_from_tutor",
                        ):
                            st.session_state.pop("sl_agent_result", None)
                            st.session_state["sl_phase"] = "reading"
                            # Reload next question
                            session_id = _id(
                                st.session_state["sl_session"]
                            )
                            try:
                                st.session_state["sl_next"] = (
                                    get_next_question(session_id)
                                )
                            except BackendApiError:
                                pass
                            st.rerun()
