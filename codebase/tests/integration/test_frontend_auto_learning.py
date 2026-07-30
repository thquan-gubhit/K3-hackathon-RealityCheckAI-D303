"""One-upload Streamlit flow from PDF to the first study question."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from frontend import api_client


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class _UploadedPdf:
    name = "lesson.pdf"
    type = "application/pdf"

    def __init__(self) -> None:
        self._content = (
            PROJECT_ROOT
            / "tests"
            / "fixtures"
            / "demo_machine_learning.pdf"
        ).read_bytes()

    def getvalue(self) -> bytes:
        return self._content


def _unit(unit_id: str, title: str, page: int) -> dict[str, object]:
    return {
        "id": unit_id,
        "title": title,
        "summary": f"Summary for {title}.",
        "learning_objectives": [f"Explain {title}"],
        "key_concepts": [title, "evidence"],
        "prerequisites": [],
        "common_misconceptions": ["Training accuracy is enough"],
        "source_pages": [page],
        "estimated_reading_minutes": 3,
        "status": "valid",
    }


def test_upload_automatically_builds_map_session_and_first_question(
    monkeypatch,
) -> None:
    calls: list[tuple[str, str]] = []
    units = [
        _unit("KU_001", "Generalization", 1),
        _unit("KU_002", "Overfitting", 2),
    ]

    monkeypatch.setattr(
        "streamlit.file_uploader",
        lambda *args, **kwargs: _UploadedPdf(),
    )
    monkeypatch.setattr(
        api_client,
        "upload_document",
        lambda filename, content, content_type: (
            calls.append(("upload", filename))
            or {
                "id": "DOC_001",
                "filename": filename,
                "status": "uploaded",
            }
        ),
    )
    monkeypatch.setattr(
        api_client,
        "process_document",
        lambda document_id: (
            calls.append(("process", document_id))
            or {
                "document": {
                    "id": document_id,
                    "filename": "lesson.pdf",
                    "status": "ready",
                    "page_count": 3,
                },
                "knowledge_units": units,
                "coverage": {
                    "readable_pages": 3,
                    "covered_pages": 3,
                    "coverage_ratio": 1.0,
                },
            }
        ),
    )
    monkeypatch.setattr(
        api_client,
        "create_learning_session",
        lambda document_id, unit_id: (
            calls.append(("session", unit_id))
            or {"id": f"SESSION_{unit_id}", "status": "active"}
        ),
    )
    monkeypatch.setattr(
        api_client,
        "get_next_question",
        lambda session_id: (
            calls.append(("question", session_id))
            or {
                "question": {
                    "id": f"QUESTION_{session_id}",
                    "question_type": "recall",
                    "question_text": "What is generalization?",
                },
                "next_action": "ASK_RECALL_QUESTION",
                "route_reason": "Establish retrieval baseline.",
            }
        ),
    )

    app = AppTest.from_file(
        PROJECT_ROOT / "frontend" / "pages" / "5_Auto_Learning.py"
    ).run(timeout=15)

    assert not app.exception
    assert calls == [
        ("upload", "lesson.pdf"),
        ("process", "DOC_001"),
        ("session", "KU_001"),
        ("question", "SESSION_KU_001"),
    ]
    assert [item.value for item in app.title] == [
        "Auto Learning — Upload một lần"
    ]
    assert "Knowledge Map" in [item.value for item in app.subheader]
    assert "Slide nguồn · Slides 1" in [
        item.value for item in app.subheader
    ]
    assert "Câu hỏi tiếp theo" in [
        item.value for item in app.subheader
    ]
    assert not any(
        button.label in {
            "Upload PDF",
            "Process selected document",
            "Start learning session",
        }
        for button in app.button
    )

    unit_selector = next(
        selector
        for selector in app.selectbox
        if selector.label == "Knowledge Unit đang học"
    )
    unit_selector.set_value("KU_002").run(timeout=15)

    assert not app.exception
    assert calls[-2:] == [
        ("session", "KU_002"),
        ("question", "SESSION_KU_002"),
    ]
    assert calls.count(("upload", "lesson.pdf")) == 1
    assert calls.count(("process", "DOC_001")) == 1
    assert "Slide nguồn · Slides 2" in [
        item.value for item in app.subheader
    ]
