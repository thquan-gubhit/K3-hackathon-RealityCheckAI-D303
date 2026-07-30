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
        st.caption("None.")


def _load_next(session_id: str) -> None:
    try:
        with st.spinner("Selecting the next activity..."):
            st.session_state["study_next"] = get_next_question(session_id)
    except BackendApiError as exc:
        _show_error("Could not select the next activity", exc)


st.set_page_config(page_title="Study Session", page_icon="🧠", layout="wide")
st.title("Study Session")
st.write(
    "Read one Knowledge Unit, hide it, answer from memory, then use the "
    "rubric-based feedback and mastery update."
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
    st.info("Process a PDF before starting a study session.")
else:
    documents = {_id(document): document for document in ready_documents}
    document_id = st.selectbox(
        "Document",
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
            "Knowledge Unit",
            options=list(units_by_id),
            format_func=lambda key: units_by_id[key].get("title", key),
        )
        unit = units_by_id[unit_id]

        if st.button("Start learning session", type="primary"):
            try:
                with st.spinner("Preparing Recall, Explain, and Apply..."):
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
                if st.button("Tôi đã đọc xong — hide the unit"):
                    st.session_state["study_read_done"] = True
                    _load_next(session_id)
                    st.rerun()
            else:
                st.info(
                    "The unit is hidden. Retrieve the answer from memory."
                )
                if "study_next" not in st.session_state:
                    if st.button("Load next question", type="primary"):
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
                            f"{str(question.get('question_type', '')).title()} "
                            "question"
                        )
                        st.write(question.get("question_text", ""))
                        answer = st.text_area(
                            "Your answer",
                            key=f"answer_{question.get('id')}",
                            height=160,
                        )
                        if st.button(
                            "Submit answer",
                            type="primary",
                            disabled=not answer.strip(),
                        ):
                            try:
                                with st.spinner(
                                    "Evaluating against the stored rubric..."
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
                                st.session_state.pop("study_next", None)
                                st.rerun()
                    elif next_activity.get("next_action") == "ACTIVATE_TUTOR_AGENT":
                        if st.button("Run Tutor Agent", type="primary"):
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
                        st.info("No normal question is pending.")

                result = st.session_state.get("study_result")
                if isinstance(result, dict):
                    evaluation = result.get("evaluation", {})
                    mastery = result.get("mastery", {})
                    st.subheader("Feedback")
                    first, second = st.columns(2)
                    with first:
                        _show_list(
                            "Correct points",
                            evaluation.get("correct_points"),
                        )
                        _show_list(
                            "Missing points",
                            evaluation.get("missing_points"),
                        )
                    with second:
                        _show_list(
                            "Incorrect points",
                            evaluation.get("incorrect_points"),
                        )
                        _show_list(
                            "Misconceptions",
                            evaluation.get("detected_misconceptions"),
                        )
                    st.write(evaluation.get("feedback", ""))
                    st.metric(
                        "Mastery",
                        f"{float(mastery.get('mastery_score', 0)):.0%}",
                    )
                    st.caption(
                        f"Next action: {result.get('next_action', 'CONTINUE')}"
                    )
                    if st.button("Continue"):
                        st.session_state.pop("study_result", None)
                        _load_next(session_id)
                        st.rerun()

                agent_result = st.session_state.get("agent_result")
                if isinstance(agent_result, dict):
                    st.subheader("Tutor Agent")
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

                if st.button("Finish unit"):
                    try:
                        finished = finish_unit(session_id)
                    except BackendApiError as exc:
                        _show_error("Unit cannot be finished yet", exc)
                    else:
                        st.success(f"Session status: {finished.get('status')}")
    else:
        st.info("The selected document has no Knowledge Units.")
