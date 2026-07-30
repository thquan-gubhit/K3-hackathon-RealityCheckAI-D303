"""End-to-end Phase 2 API test using the real PDF fixture and a fake LLM."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import TypeVar

from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import build_engine, build_session_factory, get_db, init_db
from app.main import create_app
from app.models.document import DocumentPage


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ModelT = TypeVar("ModelT", bound=BaseModel)


class FakeKnowledgeUnitLLM:
    """Return three deterministic, source-grounded candidates without network."""

    def __init__(self) -> None:
        self.calls = 0

    def generate_structured(
        self,
        messages: Sequence[Mapping[str, str]],
        response_model: type[ModelT],
        temperature: float | None = None,
    ) -> ModelT:
        self.calls += 1
        assert messages
        return response_model.model_validate(
            {
                "candidates": [
                    {
                        "candidate_id": "KU_GENERALIZATION",
                        "title": "Generalization and Data Splits",
                        "summary": (
                            "Generalization is evaluated on unseen data by "
                            "separating training, validation, and test roles."
                        ),
                        "learning_objectives": [
                            "Explain why held-out data measures generalization"
                        ],
                        "key_concepts": [
                            "generalization",
                            "validation set",
                            "test set",
                        ],
                        "concept_relations": [
                            {
                                "source": "validation set",
                                "relation": "estimates",
                                "target": "generalization",
                            }
                        ],
                        "prerequisites": [],
                        "common_misconceptions": [
                            "Training performance alone proves generalization"
                        ],
                        "source_pages": [1],
                        "estimated_reading_minutes": 3,
                    },
                    {
                        "candidate_id": "KU_OVERFITTING",
                        "title": "Overfitting Evidence",
                        "summary": (
                            "A growing training-validation gap is evidence "
                            "that a model is fitting training-specific noise."
                        ),
                        "learning_objectives": [
                            "Recognize overfitting from validation evidence"
                        ],
                        "key_concepts": [
                            "overfitting",
                            "training-validation gap",
                            "noise",
                        ],
                        "concept_relations": [
                            {
                                "source": "training-validation gap",
                                "relation": "indicates",
                                "target": "overfitting",
                            }
                        ],
                        "prerequisites": ["KU_GENERALIZATION"],
                        "common_misconceptions": [
                            "Higher training accuracy always means a better model"
                        ],
                        "source_pages": [2],
                        "estimated_reading_minutes": 3,
                    },
                    {
                        "candidate_id": "KU_REGULARIZATION",
                        "title": "Regularization and Early Stopping",
                        "summary": (
                            "Regularization and early stopping constrain "
                            "training to improve generalization."
                        ),
                        "learning_objectives": [
                            "Select a mitigation that matches overfitting evidence"
                        ],
                        "key_concepts": [
                            "regularization",
                            "early stopping",
                            "model complexity",
                        ],
                        "concept_relations": [
                            {
                                "source": "regularization",
                                "relation": "constrains",
                                "target": "model complexity",
                            }
                        ],
                        "prerequisites": ["KU_OVERFITTING"],
                        "common_misconceptions": [
                            "One mitigation works for every learning problem"
                        ],
                        "source_pages": [3],
                        "estimated_reading_minutes": 3,
                    },
                ]
            }
        )


class CoverageRepairFakeKnowledgeUnitLLM(FakeKnowledgeUnitLLM):
    """Omit one readable page once, then return a corrected complete map."""

    def __init__(self) -> None:
        super().__init__()
        self.prompts: list[str] = []

    def generate_structured(
        self,
        messages: Sequence[Mapping[str, str]],
        response_model: type[ModelT],
        temperature: float | None = None,
    ) -> ModelT:
        self.prompts.append("\n".join(item["content"] for item in messages))
        valid = super().generate_structured(
            messages,
            response_model,
            temperature,
        )
        if self.calls != 1:
            return valid
        payload = valid.model_dump(mode="json")
        payload["candidates"][2]["source_pages"] = [2]
        return response_model.model_validate(payload)


def _phase2_client(
    tmp_path: Path,
    *,
    fake_llm: FakeKnowledgeUnitLLM | None = None,
) -> tuple[TestClient, FakeKnowledgeUnitLLM, object]:
    settings = Settings(
        _env_file=None,
        app_name="Phase 2 Test",
        app_env="test",
        debug=False,
        database_url=f"sqlite:///{(tmp_path / 'phase2.db').as_posix()}",
        upload_dir=tmp_path / "uploads",
        llm_api_key="fake-key",
        llm_base_url="https://llm.invalid/v1",
        llm_model="fake-model",
    )
    engine = build_engine(settings.database_url)
    init_db(engine)
    session_factory = build_session_factory(engine)
    llm = fake_llm or FakeKnowledgeUnitLLM()
    application = create_app(settings, llm_client=llm)

    def override_database() -> Iterator[Session]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    application.dependency_overrides[get_db] = override_database
    return TestClient(application), llm, engine


def test_pdf_to_persisted_knowledge_map(tmp_path: Path) -> None:
    client, fake_llm, engine = _phase2_client(tmp_path)
    fixture = PROJECT_ROOT / "tests" / "fixtures" / "demo_machine_learning.pdf"

    try:
        with client:
            upload = client.post(
                "/documents/upload",
                files={
                    "file": (
                        "machine-learning.pdf",
                        fixture.read_bytes(),
                        "application/pdf",
                    )
                },
            )
            assert upload.status_code == 201
            uploaded = upload.json()
            assert uploaded["status"] == "uploaded"
            assert uploaded["page_count"] == 0
            assert "file_path" not in uploaded

            processed_response = client.post(
                f"/documents/{uploaded['id']}/process"
            )
            assert processed_response.status_code == 200
            processed = processed_response.json()
            assert processed["document"]["status"] == "ready"
            assert processed["document"]["page_count"] == 3
            assert len(processed["knowledge_units"]) == 3
            assert processed["coverage"] == {
                "readable_pages": 3,
                "covered_pages": 3,
                "coverage_ratio": 1.0,
            }
            assert fake_llm.calls == 1

            for unit in processed["knowledge_units"]:
                assert unit["learning_objectives"]
                assert len(unit["key_concepts"]) >= 2
                assert unit["source_pages"]
                assert "text" not in unit

            knowledge_map = client.get(
                f"/documents/{uploaded['id']}/knowledge-map"
            )
            assert knowledge_map.status_code == 200
            assert knowledge_map.json()["knowledge_units"] == (
                processed["knowledge_units"]
            )

            unit_id = processed["knowledge_units"][1]["id"]
            unit_detail = client.get(f"/knowledge-units/{unit_id}")
            assert unit_detail.status_code == 200
            prerequisite_id = unit_detail.json()["prerequisites"][0]
            assert prerequisite_id == processed["knowledge_units"][0]["id"]

            documents = client.get("/documents")
            assert documents.status_code == 200
            assert [item["id"] for item in documents.json()] == [uploaded["id"]]

        with Session(engine) as session:
            page_count = session.scalar(
                select(func.count()).select_from(DocumentPage)
            )
            assert page_count == 3
    finally:
        engine.dispose()


def test_missing_page_coverage_is_repaired_within_bound(tmp_path: Path) -> None:
    repair_llm = CoverageRepairFakeKnowledgeUnitLLM()
    client, _fake_llm, engine = _phase2_client(
        tmp_path,
        fake_llm=repair_llm,
    )
    fixture = PROJECT_ROOT / "tests" / "fixtures" / "demo_machine_learning.pdf"

    try:
        with client:
            upload = client.post(
                "/documents/upload",
                files={
                    "file": (
                        "machine-learning.pdf",
                        fixture.read_bytes(),
                        "application/pdf",
                    )
                },
            )
            processed = client.post(
                f"/documents/{upload.json()['id']}/process"
            )

        assert processed.status_code == 200
        assert processed.json()["coverage"]["coverage_ratio"] == 1.0
        assert repair_llm.calls == 2
        assert "CURRENT_MISSING_PAGES:\n[3]" in repair_llm.prompts[1]
    finally:
        engine.dispose()


def test_upload_rejects_non_pdf_with_stable_error(tmp_path: Path) -> None:
    client, _fake_llm, engine = _phase2_client(tmp_path)
    try:
        with client:
            response = client.post(
                "/documents/upload",
                files={"file": ("notes.txt", b"plain text", "text/plain")},
            )
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_FILE_TYPE"
    finally:
        engine.dispose()
