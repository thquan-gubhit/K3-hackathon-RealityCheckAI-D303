"""Idempotently seed the deterministic PDF, Knowledge Map, and questions."""

from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import get_settings  # noqa: E402
from app.database import (  # noqa: E402
    build_engine,
    build_session_factory,
    init_db,
)
from app.models.document import DocumentStatus  # noqa: E402
from app.models.question import QuestionType  # noqa: E402
from app.repositories.document_repository import DocumentRepository  # noqa: E402
from app.repositories.knowledge_unit_repository import (  # noqa: E402
    KnowledgeUnitRepository,
)
from app.repositories.question_repository import QuestionRepository  # noqa: E402
from app.schemas.knowledge_unit import KnowledgeUnitCreate  # noqa: E402
from app.schemas.question import QuestionCreate  # noqa: E402
from app.services.pdf_parser import PdfParser  # noqa: E402


DEMO_DOCUMENT_ID = "00000000-0000-0000-0000-000000000001"
DEMO_UNIT_IDS = (
    "demo-ku-generalization",
    "demo-ku-overfitting",
    "demo-ku-regularization",
)
DEMO_PDF = PROJECT_ROOT / "tests" / "fixtures" / "demo_machine_learning.pdf"


def _units() -> list[KnowledgeUnitCreate]:
    return [
        KnowledgeUnitCreate(
            id=DEMO_UNIT_IDS[0],
            document_id=DEMO_DOCUMENT_ID,
            position=1,
            title="Generalization and Data Splits",
            summary="Held-out data estimates performance on unseen examples.",
            learning_objectives=[
                "Explain why held-out data measures generalization"
            ],
            key_concepts=["generalization", "validation set", "test set"],
            concept_relations=[],
            prerequisites=[],
            common_misconceptions=[
                "Training performance alone proves generalization"
            ],
            source_pages=[1],
            estimated_reading_minutes=3,
        ),
        KnowledgeUnitCreate(
            id=DEMO_UNIT_IDS[1],
            document_id=DEMO_DOCUMENT_ID,
            position=2,
            title="Overfitting Evidence",
            summary="A training-validation gap can reveal overfitting.",
            learning_objectives=[
                "Recognize overfitting from validation evidence"
            ],
            key_concepts=["overfitting", "training-validation gap", "noise"],
            concept_relations=[],
            prerequisites=[DEMO_UNIT_IDS[0]],
            common_misconceptions=[
                "Higher training accuracy always means a better model"
            ],
            source_pages=[2],
            estimated_reading_minutes=3,
        ),
        KnowledgeUnitCreate(
            id=DEMO_UNIT_IDS[2],
            document_id=DEMO_DOCUMENT_ID,
            position=3,
            title="Regularization and Early Stopping",
            summary="Training controls can reduce overfitting.",
            learning_objectives=[
                "Select a mitigation that matches overfitting evidence"
            ],
            key_concepts=[
                "regularization",
                "early stopping",
                "model complexity",
            ],
            concept_relations=[],
            prerequisites=[DEMO_UNIT_IDS[1]],
            common_misconceptions=[
                "One mitigation works for every learning problem"
            ],
            source_pages=[3],
            estimated_reading_minutes=3,
        ),
    ]


def _rubric(reference_point: str) -> dict[str, object]:
    return {
        "required_points": [{"point": reference_point, "weight": 1.0}],
        "optional_points": [],
        "acceptable_alternatives": [],
        "misconceptions": [
            "Training accuracy alone proves model quality"
        ],
        "dimension_weights": {
            "correctness": 0.35,
            "coverage": 0.25,
            "reasoning": 0.25,
            "application": 0.15,
        },
    }


def _questions(unit: KnowledgeUnitCreate) -> list[QuestionCreate]:
    objective = unit.learning_objectives[0]
    page = unit.source_pages
    specifications = (
        (
            QuestionType.RECALL,
            "easy",
            f"What is the central idea of {unit.title}?",
            unit.summary,
        ),
        (
            QuestionType.EXPLAIN,
            "medium",
            f"Explain why {unit.title} matters for model generalization.",
            f"{unit.summary} The explanation should connect evidence to "
            "performance on unseen data.",
        ),
        (
            QuestionType.APPLY,
            "hard",
            f"How would you apply {unit.title} when diagnosing a model?",
            f"Use the source evidence about {unit.title} to identify the "
            "relevant signal and choose a justified action.",
        ),
    )
    return [
        QuestionCreate(
            id=f"demo-{unit.position}-{question_type.value}",
            knowledge_unit_id=unit.id,
            learning_objective=objective,
            question_type=question_type,
            difficulty=difficulty,
            question_text=question_text,
            reference_answer=reference_answer,
            rubric=_rubric(reference_answer),
            source_pages=page,
        )
        for question_type, difficulty, question_text, reference_answer in specifications
    ]


def seed_demo(database_url: str | None = None) -> tuple[int, int]:
    """Seed one ready document and return unit/question counts."""

    if not DEMO_PDF.is_file():
        raise FileNotFoundError(f"Demo fixture is missing: {DEMO_PDF}")
    settings = get_settings()
    engine = build_engine(database_url or settings.database_url)
    init_db(engine)
    session_factory = build_session_factory(engine)
    parsed = PdfParser().parse(DEMO_PDF)

    try:
        with session_factory() as session:
            documents = DocumentRepository(session)
            document = documents.get(DEMO_DOCUMENT_ID)
            if document is None:
                documents.create(
                    document_id=DEMO_DOCUMENT_ID,
                    filename=DEMO_PDF.name,
                    file_path=str(DEMO_PDF),
                    page_count=parsed.page_count,
                    status=DocumentStatus.READY,
                )
            documents.upsert_pages(DEMO_DOCUMENT_ID, parsed.pages)

            unit_repository = KnowledgeUnitRepository(session)
            units = unit_repository.list_for_document(DEMO_DOCUMENT_ID)
            if not units:
                units = unit_repository.replace_for_document(
                    DEMO_DOCUMENT_ID,
                    _units(),
                )

            question_repository = QuestionRepository(session)
            question_count = 0
            unit_payloads = {unit.id: unit for unit in _units()}
            for unit in units:
                existing = question_repository.list_for_unit(unit.id)
                existing_types = {item.question_type for item in existing}
                for payload in _questions(unit_payloads[unit.id]):
                    if payload.question_type.value not in existing_types:
                        question_repository.create(payload)
                question_count += len(
                    question_repository.list_for_unit(unit.id)
                )

            documents.update_status(
                DEMO_DOCUMENT_ID,
                DocumentStatus.READY,
            )
            session.commit()
            return len(units), question_count
    finally:
        engine.dispose()


def main() -> int:
    units, questions = seed_demo()
    print(
        "Demo seed ready: "
        f"document={DEMO_DOCUMENT_ID} units={units} questions={questions}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
