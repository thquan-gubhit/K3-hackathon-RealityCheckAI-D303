"""Threshold, coverage, and duplicate tests for Phase 2 KU rules."""

from __future__ import annotations

from app.config import Settings
from app.rules.knowledge_unit_rules import (
    AdjacentUnitSignals,
    KnowledgeUnitAction,
    compute_adjacent_signals,
    evaluate_knowledge_unit,
    validate_duplicate_units,
    validate_source_coverage,
)
from app.schemas.knowledge_unit import KnowledgeUnitCandidate


def _settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "_env_file": None,
        "llm_api_key": "unit-test-key",
        "llm_base_url": "https://llm.invalid/v1",
        "llm_model": "unit-test-model",
        "ku_min_concepts": 2,
        "ku_max_concepts": 7,
        "ku_max_learning_objectives": 3,
        "ku_min_reading_minutes": 2,
        "ku_max_reading_minutes": 10,
        "ku_max_refinement_rounds": 2,
    }
    values.update(overrides)
    return Settings(**values)  # type: ignore[arg-type]


def _candidate(**overrides: object) -> KnowledgeUnitCandidate:
    values: dict[str, object] = {
        "candidate_id": "KU_CANDIDATE_01",
        "title": "Overfitting and generalization",
        "summary": "How training fit differs from performance on unseen data.",
        "learning_objectives": ["Explain overfitting"],
        "key_concepts": ["overfitting", "generalization"],
        "concept_relations": [
            {
                "source": "training-validation gap",
                "relation": "indicates",
                "target": "overfitting",
            }
        ],
        "prerequisites": [],
        "common_misconceptions": [
            "High training accuracy always proves good generalization"
        ],
        "source_pages": [2, 3],
        "estimated_reading_minutes": 5,
        "has_independent_objective": True,
        "is_only_example": False,
        "can_generate_independent_question": True,
    }
    values.update(overrides)
    return KnowledgeUnitCandidate.model_validate(values)


def test_split_when_too_many_objectives() -> None:
    candidate = _candidate(
        learning_objectives=["Objective 1", "Objective 2", "Objective 3", "Objective 4"]
    )

    decision = evaluate_knowledge_unit(candidate, _settings())

    assert decision.action is KnowledgeUnitAction.SPLIT
    assert "KU-SPLIT-001" in decision.triggered_rules


def test_split_when_too_many_concepts() -> None:
    candidate = _candidate(key_concepts=[f"concept {index}" for index in range(8)])

    decision = evaluate_knowledge_unit(candidate, _settings())

    assert decision.action is KnowledgeUnitAction.SPLIT
    assert decision.triggered_rules == ("KU-SPLIT-002",)


def test_split_when_too_long() -> None:
    decision = evaluate_knowledge_unit(
        _candidate(estimated_reading_minutes=11),
        _settings(),
    )

    assert decision.action is KnowledgeUnitAction.SPLIT
    assert decision.triggered_rules == ("KU-SPLIT-003",)


def test_exact_split_thresholds_are_accepted() -> None:
    candidate = _candidate(
        learning_objectives=["Objective 1", "Objective 2", "Objective 3"],
        key_concepts=[f"concept {index}" for index in range(7)],
        estimated_reading_minutes=10,
    )

    assert (
        evaluate_knowledge_unit(candidate, _settings()).action
        is KnowledgeUnitAction.ACCEPT
    )


def test_merge_small_unit_without_objective() -> None:
    candidate = _candidate(
        key_concepts=["overfitting"],
        has_independent_objective=False,
    )

    decision = evaluate_knowledge_unit(candidate, _settings())

    assert decision.action is KnowledgeUnitAction.MERGE
    assert decision.triggered_rules == ("KU-MERGE-001",)


def test_small_unit_with_independent_objective_is_accepted() -> None:
    candidate = _candidate(
        key_concepts=["overfitting"],
        has_independent_objective=True,
    )

    assert (
        evaluate_knowledge_unit(candidate, _settings()).action
        is KnowledgeUnitAction.ACCEPT
    )


def test_merge_short_example() -> None:
    candidate = _candidate(
        estimated_reading_minutes=1,
        is_only_example=True,
    )

    decision = evaluate_knowledge_unit(candidate, _settings())

    assert decision.action is KnowledgeUnitAction.MERGE
    assert decision.triggered_rules == ("KU-MERGE-002",)


def test_short_non_example_is_accepted_at_merge_boundary() -> None:
    candidate = _candidate(
        estimated_reading_minutes=1,
        is_only_example=False,
    )

    assert (
        evaluate_knowledge_unit(candidate, _settings()).action
        is KnowledgeUnitAction.ACCEPT
    )


def test_merge_unassessable_unit() -> None:
    decision = evaluate_knowledge_unit(
        _candidate(can_generate_independent_question=False),
        _settings(),
    )

    assert decision.action is KnowledgeUnitAction.MERGE
    assert decision.triggered_rules == ("KU-MERGE-003",)


def test_merge_overlapping_adjacent_units() -> None:
    adjacent = AdjacentUnitSignals(
        topic_similarity_is_high=True,
        learning_objectives_overlap_is_high=True,
        topic_similarity=0.9,
        learning_objective_overlap=0.8,
    )

    decision = evaluate_knowledge_unit(
        _candidate(),
        _settings(),
        adjacent=adjacent,
    )

    assert decision.action is KnowledgeUnitAction.MERGE
    assert decision.triggered_rules == ("KU-MERGE-004",)


def test_adjacent_signal_threshold_is_inclusive() -> None:
    left = _candidate()
    right = _candidate(candidate_id="KU_CANDIDATE_02", source_pages=[4])

    signals = compute_adjacent_signals(
        left,
        right,
        high_similarity_threshold=1.0,
    )

    assert signals.topic_similarity_is_high is True
    assert signals.learning_objectives_overlap_is_high is True


def test_refinement_stops_at_limit() -> None:
    decision = evaluate_knowledge_unit(
        _candidate(estimated_reading_minutes=11),
        _settings(),
        refinement_round=2,
    )

    assert decision.action is KnowledgeUnitAction.STOP_INVALID
    assert decision.triggered_rules == ("KU-SPLIT-003", "KU-LIMIT-001")


def test_valid_candidate_is_accepted_at_refinement_limit() -> None:
    decision = evaluate_knowledge_unit(
        _candidate(),
        _settings(),
        refinement_round=2,
    )

    assert decision.action is KnowledgeUnitAction.ACCEPT


def test_coverage_accepts_documented_exclusion() -> None:
    units = [
        _candidate(source_pages=[1, 2]),
        _candidate(candidate_id="KU_CANDIDATE_02", source_pages=[4]),
    ]

    result = validate_source_coverage(
        units,
        {1, 2, 3, 4},
        excluded_pages={3: "Table of contents only"},
    )

    assert result.is_valid is True
    assert result.covered_pages == (1, 2, 4)
    assert result.excluded_pages == (3,)


def test_coverage_rejects_missing_unexpected_and_unexplained_pages() -> None:
    result = validate_source_coverage(
        [_candidate(source_pages=[1, 5])],
        {1, 2, 3},
        excluded_pages={3: ""},
    )

    assert result.is_valid is False
    assert result.missing_pages == (2, 3)
    assert result.unexpected_pages == (5,)
    assert result.invalid_exclusions == (3,)


def test_serious_duplicate_units_are_rejected() -> None:
    units = [
        _candidate(),
        _candidate(candidate_id="KU_CANDIDATE_02", source_pages=[4]),
    ]

    result = validate_duplicate_units(units)

    assert result.is_valid is False
    assert len(result.pairs) == 1
    assert result.pairs[0].left_index == 0
    assert result.pairs[0].right_index == 1


def test_distinct_units_are_not_duplicates() -> None:
    result = validate_duplicate_units(
        [
            _candidate(),
            _candidate(
                candidate_id="KU_CANDIDATE_02",
                title="L1 regularization",
                learning_objectives=["Compare sparse and dense model weights"],
                key_concepts=["L1 penalty", "sparsity"],
                source_pages=[4],
            ),
        ]
    )

    assert result.is_valid is True
    assert result.pairs == ()
