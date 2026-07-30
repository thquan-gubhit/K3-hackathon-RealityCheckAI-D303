"""Streamlit rendering tests for the Phase 2 transport pages."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

from frontend import api_client


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_upload_page_renders_available_document(monkeypatch) -> None:
    monkeypatch.setattr(
        api_client,
        "list_documents",
        lambda: [
            {
                "id": "DOC_001",
                "original_filename": "lesson.pdf",
                "status": "uploaded",
                "page_count": None,
            }
        ],
    )

    app = AppTest.from_file(
        PROJECT_ROOT / "frontend" / "pages" / "1_Upload_Document.py"
    ).run(timeout=10)

    assert not app.exception
    assert [item.value for item in app.title] == ["Upload Document"]
    assert [item.label for item in app.selectbox] == ["Document"]
    assert "lesson.pdf" in app.selectbox[0].format_func("DOC_001")


def test_knowledge_map_page_loads_and_renders_unit_fields(monkeypatch) -> None:
    monkeypatch.setattr(
        api_client,
        "list_documents",
        lambda: [
            {
                "id": "DOC_001",
                "original_filename": "lesson.pdf",
                "status": "processed",
            }
        ],
    )
    monkeypatch.setattr(
        api_client,
        "get_knowledge_map",
        lambda document_id: {
            "document_id": document_id,
            "status": "ready",
            "knowledge_units": [
                {
                    "id": "KU_001",
                    "title": "Generalization",
                    "summary": "How models perform on unseen data.",
                    "learning_objectives": ["Explain generalization"],
                    "key_concepts": ["training data", "validation data"],
                    "concept_relations": [
                        {
                            "source": "validation data",
                            "relation": "measures",
                            "target": "generalization",
                        }
                    ],
                    "prerequisites": [],
                    "common_misconceptions": ["Training accuracy is enough"],
                    "source_pages": [1, 2],
                    "estimated_reading_minutes": 4,
                    "status": "valid",
                }
            ],
        },
    )

    app = AppTest.from_file(
        PROJECT_ROOT / "frontend" / "pages" / "2_Knowledge_Map.py"
    ).run(timeout=10)
    app.button[0].click().run(timeout=10)

    assert not app.exception
    assert [item.value for item in app.title] == ["Knowledge Map"]
    assert "Knowledge Units (1)" in [
        item.value for item in app.subheader
    ]
    assert any(
        "Generalization" in expander.label for expander in app.expander
    )
    assert "**Learning objectives**" in [
        item.value for item in app.markdown
    ]
