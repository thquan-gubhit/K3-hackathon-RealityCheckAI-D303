"""Question rubric and deterministic validation tests for Phase 3."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.rules.question_rules import validate_question_candidate
from app.schemas.knowledge_unit import KnowledgeUnitContent
from app.schemas.question import QuestionCandidate, QuestionRubric


def _rubric() -> dict[str, object]:
    return {
        "required_points": [
            {"point": "Identifies overfitting", "weight": 0.6},
            {"point": "Uses validation evidence", "weight": 0.3},
        ],
        "optional_points": [
            {"point": "Suggests mitigation", "weight": 0.1}
        ],
        "acceptable_alternatives": ["regularization"],
        "misconceptions": ["Training accuracy alone proves quality"],
        "dimension_weights": {
            "correctness": 0.35,
            "coverage": 0.25,
            "reasoning": 0.25,
            "application": 0.15,
        },
    }


def _unit() -> KnowledgeUnitContent:
    return KnowledgeUnitContent(
        title="Overfitting",
        summary="Validation evidence reveals weak generalization.",
        learning_objectives=["Recognize evidence of overfitting"],
        key_concepts=["overfitting", "validation gap"],
        source_pages=[2],
        estimated_reading_minutes=3,
    )


def _candidate(**overrides: object) -> QuestionCandidate:
    values: dict[str, object] = {
        "candidate_id": "Q_CANDIDATE_1",
        "learning_objective": "Recognize evidence of overfitting",
        "question_type": "apply",
        "difficulty": "medium",
        "question_text": (
            "A model improves on training data while validation degrades. "
            "What is happening and what evidence supports it?"
        ),
        "reference_answer": (
            "The divergence indicates overfitting and weak generalization."
        ),
        "rubric": _rubric(),
        "source_pages": [2],
        "source_grounded": True,
        "objective_aligned": True,
        "answer_leak": False,
        "ambiguous": False,
        "requires_external_knowledge": False,
    }
    values.update(overrides)
    return QuestionCandidate.model_validate(values)


def test_valid_question_candidate_is_accepted() -> None:
    decision = validate_question_candidate(_candidate(), _unit())

    assert decision.accepted is True
    assert decision.reasons == ()
    assert len(decision.content_fingerprint) == 64


def test_question_validation_rejects_all_semantic_failures() -> None:
    decision = validate_question_candidate(
        _candidate(
            source_grounded=False,
            objective_aligned=False,
            learning_objective="Unrelated objective",
            answer_leak=True,
            ambiguous=True,
            requires_external_knowledge=True,
            source_pages=[99],
        ),
        _unit(),
    )

    assert decision.accepted is False
    assert set(decision.reasons) == {
        "NOT_SOURCE_GROUNDED",
        "OBJECTIVE_MISMATCH",
        "ANSWER_LEAK",
        "AMBIGUOUS",
        "EXTERNAL_KNOWLEDGE_REQUIRED",
    }


def test_question_validation_rejects_material_duplicate() -> None:
    candidate = _candidate()
    decision = validate_question_candidate(
        candidate,
        _unit(),
        existing_question_texts=[candidate.question_text],
    )

    assert decision.reasons == ("DUPLICATE",)


def test_rubric_rejects_non_normalized_point_weights() -> None:
    payload = _rubric()
    payload["optional_points"] = [
        {"point": "Suggests mitigation", "weight": 0.2}
    ]

    with pytest.raises(ValidationError):
        QuestionRubric.model_validate(payload)


def test_rubric_rejects_non_normalized_dimension_weights() -> None:
    payload = _rubric()
    payload["dimension_weights"] = {
        "correctness": 0.5,
        "coverage": 0.5,
        "reasoning": 0.5,
        "application": 0.5,
    }

    with pytest.raises(ValidationError):
        QuestionRubric.model_validate(payload)
