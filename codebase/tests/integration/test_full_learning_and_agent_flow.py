"""Offline acceptance flow across document, assessment, mastery, and agent."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import TypeVar

from fastapi.testclient import TestClient
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config import Settings
from app.database import build_engine, build_session_factory, get_db, init_db
from app.main import create_app
from app.models.question import Question
from app.schemas.agent import AgentAction
from app.schemas.evaluation import AnswerEvaluation
from app.schemas.knowledge_unit import KnowledgeUnitBatch
from app.schemas.question import QuestionBatch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ModelT = TypeVar("ModelT", bound=BaseModel)


def _rubric() -> dict[str, object]:
    return {
        "required_points": [
            {"point": "States the core source-grounded idea", "weight": 1.0}
        ],
        "optional_points": [],
        "acceptable_alternatives": [],
        "misconceptions": ["Training accuracy alone proves model quality"],
        "dimension_weights": {
            "correctness": 0.35,
            "coverage": 0.25,
            "reasoning": 0.25,
            "application": 0.15,
        },
    }


class FullFlowFakeLLM:
    """Return typed fixtures keyed by response model, never by provider calls."""

    def __init__(self) -> None:
        self.calls: Counter[str] = Counter()

    def generate_structured(
        self,
        messages: Sequence[Mapping[str, str]],
        response_model: type[ModelT],
        temperature: float | None = None,
    ) -> ModelT:
        self.calls[response_model.__name__] += 1
        text = "\n".join(message["content"] for message in messages).casefold()

        if response_model is KnowledgeUnitBatch:
            payload: object = {
                "candidates": [
                    {
                        "candidate_id": "KU_GENERALIZATION",
                        "title": "Generalization and Data Splits",
                        "summary": "Held-out data estimates performance on unseen data.",
                        "learning_objectives": [
                            "Explain why held-out data measures generalization"
                        ],
                        "key_concepts": [
                            "generalization",
                            "validation set",
                            "test set",
                        ],
                        "concept_relations": [],
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
                        "summary": "A train-validation gap indicates overfitting.",
                        "learning_objectives": [
                            "Recognize overfitting from validation evidence"
                        ],
                        "key_concepts": [
                            "overfitting",
                            "training-validation gap",
                        ],
                        "concept_relations": [],
                        "prerequisites": ["KU_GENERALIZATION"],
                        "common_misconceptions": [
                            "Training accuracy alone proves model quality"
                        ],
                        "source_pages": [2],
                        "estimated_reading_minutes": 3,
                    },
                    {
                        "candidate_id": "KU_REGULARIZATION",
                        "title": "Regularization and Early Stopping",
                        "summary": "Training controls can improve generalization.",
                        "learning_objectives": [
                            "Select a mitigation for overfitting evidence"
                        ],
                        "key_concepts": ["regularization", "early stopping"],
                        "concept_relations": [],
                        "prerequisites": ["KU_OVERFITTING"],
                        "common_misconceptions": [
                            "One mitigation works in every setting"
                        ],
                        "source_pages": [3],
                        "estimated_reading_minutes": 3,
                    },
                ]
            }
        elif response_model is QuestionBatch:
            objective = "Explain why held-out data measures generalization"
            payload = {
                "candidates": [
                    {
                        "candidate_id": "Q_RECALL",
                        "learning_objective": objective,
                        "question_type": "recall",
                        "difficulty": "easy",
                        "question_text": (
                            "What does generalization describe for a learned model?"
                        ),
                        "reference_answer": (
                            "It describes performance on unseen data."
                        ),
                        "rubric": _rubric(),
                        "source_pages": [1],
                        "source_grounded": True,
                        "objective_aligned": True,
                    },
                    {
                        "candidate_id": "Q_EXPLAIN",
                        "learning_objective": objective,
                        "question_type": "explain",
                        "difficulty": "medium",
                        "question_text": (
                            "Explain why validation data should be separate "
                            "from training data."
                        ),
                        "reference_answer": (
                            "Separation provides evidence about unseen-data "
                            "performance instead of training fit."
                        ),
                        "rubric": _rubric(),
                        "source_pages": [1],
                        "source_grounded": True,
                        "objective_aligned": True,
                    },
                    {
                        "candidate_id": "Q_APPLY",
                        "learning_objective": objective,
                        "question_type": "apply",
                        "difficulty": "hard",
                        "question_text": (
                            "A team tunes on one split repeatedly. Which held-out "
                            "split should provide the final generalization check?"
                        ),
                        "reference_answer": (
                            "The untouched test set should provide the final check."
                        ),
                        "rubric": _rubric(),
                        "source_pages": [1],
                        "source_grounded": True,
                        "objective_aligned": True,
                    },
                ]
            }
        elif response_model is AnswerEvaluation:
            if "uncertain answer" in text:
                payload = {
                    "overall_score": 0.2,
                    "dimension_scores": {
                        "correctness": 0.2,
                        "coverage": 0.2,
                        "reasoning": 0.2,
                        "application": 0.2,
                    },
                    "correct_points": [],
                    "missing_points": ["Needs clarification"],
                    "incorrect_points": [],
                    "contradictions": [],
                    "detected_misconceptions": [
                        "Training accuracy alone proves model quality"
                    ],
                    "feedback": "Please clarify what evidence you mean.",
                    "recommended_next_action": "REMEDIATE",
                    "confidence": 0.2,
                }
            elif "misconception answer" in text:
                payload = {
                    "overall_score": 0.1,
                    "dimension_scores": {
                        "correctness": 0.1,
                        "coverage": 0.1,
                        "reasoning": 0.1,
                        "application": 0.1,
                    },
                    "correct_points": [],
                    "missing_points": ["Missing held-out evidence"],
                    "incorrect_points": ["Claims training accuracy is sufficient"],
                    "contradictions": ["Contradicts the held-out evaluation role"],
                    "detected_misconceptions": [
                        "Training accuracy alone proves model quality"
                    ],
                    "feedback": "Use held-out evidence, not training fit alone.",
                    "recommended_next_action": "REMEDIATE",
                    "confidence": 0.95,
                }
            elif "incomplete answer" in text:
                payload = {
                    "overall_score": 0.5,
                    "dimension_scores": {
                        "correctness": 0.8,
                        "coverage": 0.4,
                        "reasoning": 0.4,
                        "application": 0.2,
                    },
                    "correct_points": ["Mentions held-out data"],
                    "missing_points": ["Does not explain separation"],
                    "incorrect_points": [],
                    "contradictions": [],
                    "detected_misconceptions": [],
                    "feedback": "Explain why separation matters.",
                    "recommended_next_action": "ASK_EXPLAIN_QUESTION",
                    "confidence": 0.9,
                }
            else:
                payload = {
                    "overall_score": 0.95,
                    "dimension_scores": {
                        "correctness": 1.0,
                        "coverage": 1.0,
                        "reasoning": 0.9,
                        "application": 0.8,
                    },
                    "correct_points": ["Correct held-out evaluation role"],
                    "missing_points": [],
                    "incorrect_points": [],
                    "contradictions": [],
                    "detected_misconceptions": [],
                    "feedback": "Correct and well grounded.",
                    "recommended_next_action": "CONTINUE",
                    "confidence": 0.95,
                }
        elif response_model is AgentAction:
            payload = {
                "reason": "Provide a bounded cue tied to the current concept.",
                "action": "give_hint",
                "arguments": {"concept": "generalization"},
                "stop": False,
            }
        else:
            raise AssertionError(f"Unexpected response model: {response_model}")
        return response_model.model_validate(payload)


def _client(
    tmp_path: Path,
    *,
    agent_enabled: bool = True,
) -> tuple[TestClient, FullFlowFakeLLM, object]:
    settings = Settings(
        _env_file=None,
        app_name="Full Flow Test",
        app_env="test",
        debug=False,
        database_url=f"sqlite:///{(tmp_path / 'full-flow.db').as_posix()}",
        upload_dir=tmp_path / "uploads",
        llm_api_key="fake-key",
        llm_base_url="https://llm.invalid/v1",
        llm_model="fake-model",
        agent_enabled=agent_enabled,
        agent_max_steps=2,
    )
    engine = build_engine(settings.database_url)
    init_db(engine)
    session_factory = build_session_factory(engine)
    fake_llm = FullFlowFakeLLM()
    application = create_app(settings, llm_client=fake_llm)

    def override_database() -> Iterator[Session]:
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    application.dependency_overrides[get_db] = override_database
    return TestClient(application), fake_llm, engine


def _prepare_document(client: TestClient) -> tuple[str, str]:
    fixture = PROJECT_ROOT / "tests" / "fixtures" / "demo_machine_learning.pdf"
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
    document_id = upload.json()["id"]
    processed = client.post(f"/documents/{document_id}/process")
    assert processed.status_code == 200
    return document_id, processed.json()["knowledge_units"][0]["id"]


def _answer(
    client: TestClient,
    session_id: str,
    answer: str,
) -> dict[str, object]:
    next_question = client.get(
        f"/learning-sessions/{session_id}/next-question"
    )
    assert next_question.status_code == 200
    question = next_question.json()["question"]
    assert question is not None
    assert "reference_answer" not in question
    assert "rubric" not in question
    response = client.post(
        f"/learning-sessions/{session_id}/answers",
        json={"question_id": question["id"], "user_answer": answer},
    )
    assert response.status_code == 200
    return response.json()


def test_complete_phase_3_to_5_acceptance_flow(tmp_path: Path) -> None:
    client, fake_llm, engine = _client(tmp_path)
    try:
        with client:
            document_id, unit_id = _prepare_document(client)

            generated = client.post(
                f"/knowledge-units/{unit_id}/generate-questions"
            )
            assert generated.status_code == 200
            questions = generated.json()["questions"]
            assert {item["question_type"] for item in questions} == {
                "recall",
                "explain",
                "apply",
            }
            assert all("reference_answer" not in item for item in questions)
            assert all("rubric" not in item for item in questions)

            created = client.post(
                "/learning-sessions",
                json={
                    "user_id": "local-user",
                    "document_id": document_id,
                    "knowledge_unit_id": unit_id,
                },
            )
            assert created.status_code == 201
            session_id = created.json()["id"]

            strong = _answer(client, session_id, "strong answer")
            assert strong["evaluation"]["correct_points"]
            assert strong["attempt"]["understanding_state"] == "strong_answer"
            mastery_scores = [strong["mastery"]["mastery_score"]]

            incomplete = _answer(client, session_id, "incomplete answer")
            assert incomplete["evaluation"]["missing_points"]
            mastery_scores.append(incomplete["mastery"]["mastery_score"])

            misconception = _answer(
                client,
                session_id,
                "misconception answer",
            )
            assert misconception["evaluation"]["incorrect_points"]
            assert misconception["evaluation"]["detected_misconceptions"]
            mastery_scores.append(misconception["mastery"]["mastery_score"])

            repeated = _answer(
                client,
                session_id,
                "misconception answer repeated",
            )
            assert repeated["next_action"] == "ACTIVATE_TUTOR_AGENT"
            assert repeated["misconceptions"][0]["occurrence_count"] == 2
            mastery_scores.append(repeated["mastery"]["mastery_score"])
            assert len(set(mastery_scores)) == 4

            progress = client.get("/progress/local-user")
            assert progress.status_code == 200
            unit_progress = next(
                item
                for item in progress.json()["knowledge_units"]
                if item["knowledge_unit_id"] == unit_id
            )
            assert unit_progress["answered_questions"] == 3
            assert unit_progress["active_misconceptions"][0][
                "occurrence_count"
            ] == 2

            agent = client.post(
                f"/learning-sessions/{session_id}/agent/run",
                json={"reason": "REPEATED_MISCONCEPTION"},
            )
            assert agent.status_code == 200
            assert agent.json()["status"] == "max_steps"
            assert len(agent.json()["steps"]) == 2
            assert all(
                step["action"] == "give_hint"
                for step in agent.json()["steps"]
            )

            traces = client.get(
                f"/learning-sessions/{session_id}/agent/traces"
            )
            assert traces.status_code == 200
            assert len(traces.json()) == 2
            assert all("api_key" not in str(item).casefold() for item in traces.json())

        assert fake_llm.calls["KnowledgeUnitBatch"] == 1
        assert fake_llm.calls["QuestionBatch"] == 1
        assert fake_llm.calls["AnswerEvaluation"] == 4
        assert fake_llm.calls["AgentAction"] == 2
        with Session(engine) as database:
            persisted_questions = database.query(Question).all()
            assert len(persisted_questions) == 3
            assert all(item.reference_answer for item in persisted_questions)
            assert all(item.rubric["required_points"] for item in persisted_questions)
            assert all(item.rubric_version == 1 for item in persisted_questions)
    finally:
        engine.dispose()


def test_agent_disabled_preserves_normal_learning_workflow(tmp_path: Path) -> None:
    client, _fake_llm, engine = _client(tmp_path, agent_enabled=False)
    try:
        with client:
            document_id, unit_id = _prepare_document(client)
            created = client.post(
                "/learning-sessions",
                json={
                    "document_id": document_id,
                    "knowledge_unit_id": unit_id,
                },
            )
            assert created.status_code == 201
            session_id = created.json()["id"]

            next_question = client.get(
                f"/learning-sessions/{session_id}/next-question"
            )
            assert next_question.status_code == 200
            assert next_question.json()["question"]["question_type"] == "recall"

            uncertain = client.post(
                f"/learning-sessions/{session_id}/answers",
                json={
                    "question_id": next_question.json()["question"]["id"],
                    "user_answer": "uncertain answer",
                },
            )
            assert uncertain.status_code == 200
            assert (
                uncertain.json()["evaluation"]["recommended_next_action"]
                == "ASK_CLARIFICATION"
            )
            assert not uncertain.json()["evaluation"][
                "detected_misconceptions"
            ]

            disabled = client.post(
                f"/learning-sessions/{session_id}/agent/run",
                json={"reason": "EXPLICIT_DIFFERENT_EXPLANATION"},
            )
            assert disabled.status_code == 409
            assert disabled.json()["error"]["code"] == "AGENT_DISABLED"
    finally:
        engine.dispose()
