"""Streamlit render tests for study and progress pages."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from frontend import api_client


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _unit() -> dict[str, object]:
    return {
        "id": "KU_001",
        "title": "Generalization",
        "summary": "How models perform on unseen data.",
        "learning_objectives": ["Explain held-out evaluation"],
        "key_concepts": ["generalization", "validation set"],
        "prerequisites": [],
        "common_misconceptions": ["Training accuracy is sufficient"],
        "source_pages": [1],
        "estimated_reading_minutes": 3,
        "status": "valid",
    }


def test_study_page_starts_and_displays_unit(monkeypatch) -> None:
    monkeypatch.setattr(
        api_client,
        "list_documents",
        lambda: [
            {
                "id": "DOC_001",
                "filename": "lesson.pdf",
                "status": "ready",
            }
        ],
    )
    monkeypatch.setattr(
        api_client,
        "get_knowledge_map",
        lambda _document_id: {
            "document_id": "DOC_001",
            "status": "ready",
            "knowledge_units": [_unit()],
        },
    )
    monkeypatch.setattr(
        api_client,
        "create_learning_session",
        lambda _document_id, _unit_id: {
            "id": "SESSION_001",
            "status": "active",
        },
    )

    app = AppTest.from_file(
        PROJECT_ROOT / "frontend" / "pages" / "3_Study_Session.py"
    ).run(timeout=10)
    app.button[0].click().run(timeout=10)

    assert not app.exception
    assert [item.value for item in app.title] == ["Study Session"]
    assert "Generalization" in [item.value for item in app.subheader]
    assert any(
        "Tôi đã đọc xong" in button.label for button in app.button
    )


def test_progress_dashboard_renders_dimensions(monkeypatch) -> None:
    monkeypatch.setattr(
        api_client,
        "get_progress",
        lambda user_id: {
            "user_id": user_id,
            "recommended_next_unit_id": "KU_001",
            "knowledge_units": [
                {
                    "knowledge_unit_id": "KU_001",
                    "title": "Generalization",
                    "position": 1,
                    "mastery": {
                        "recall_score": 0.7,
                        "understanding_score": 0.6,
                        "application_score": 0.4,
                        "mastery_score": 0.55,
                        "status": "in_progress",
                        "question_evidence_count": 2,
                    },
                    "answered_questions": 2,
                    "active_misconceptions": [],
                }
            ],
        },
    )

    app = AppTest.from_file(
        PROJECT_ROOT / "frontend" / "pages" / "4_Progress_Dashboard.py"
    ).run(timeout=10)
    app.button[0].click().run(timeout=10)

    assert not app.exception
    assert [item.value for item in app.title] == ["Progress Dashboard"]
    assert "Knowledge Units (1)" in [
        item.value for item in app.subheader
    ]
    assert any(expander.label.startswith("1. Generalization") for expander in app.expander)
