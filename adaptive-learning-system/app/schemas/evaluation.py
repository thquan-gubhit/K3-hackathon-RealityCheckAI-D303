"""Structured answer-evaluation and feedback contracts."""

from __future__ import annotations

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class DimensionScores(BaseModel):
    """Four evidence dimensions constrained to the unit interval."""

    model_config = ConfigDict(extra="forbid")

    correctness: float = Field(ge=0.0, le=1.0)
    coverage: float = Field(ge=0.0, le=1.0)
    reasoning: float = Field(ge=0.0, le=1.0)
    application: float = Field(ge=0.0, le=1.0)


class AnswerEvaluation(BaseModel):
    """LLM-produced evidence parsed before deterministic score handling."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    overall_score: float = Field(ge=0.0, le=1.0)
    dimension_scores: DimensionScores
    correct_points: list[str] = Field(default_factory=list, max_length=50)
    missing_points: list[str] = Field(default_factory=list, max_length=50)
    incorrect_points: list[str] = Field(default_factory=list, max_length=50)
    contradictions: list[str] = Field(default_factory=list, max_length=50)
    detected_misconceptions: list[str] = Field(
        default_factory=list,
        max_length=50,
    )
    feedback: str = Field(min_length=1, max_length=10_000)
    recommended_next_action: str = Field(min_length=1, max_length=100)
    confidence: float = Field(ge=0.0, le=1.0)

    @field_validator(
        "correct_points",
        "missing_points",
        "incorrect_points",
        "contradictions",
        "detected_misconceptions",
    )
    @classmethod
    def normalize_evidence(cls, values: list[str]) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()
        for value in values:
            item = value.strip()
            if not item:
                raise ValueError("evidence entries must be non-empty")
            if item.casefold() not in seen:
                seen.add(item.casefold())
                normalized.append(item)
        return normalized


class AnswerSubmission(BaseModel):
    """Learner response: free text."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    question_id: str = Field(min_length=1, max_length=100)
    user_answer: str = Field(min_length=1, max_length=20_000)


__all__ = ["AnswerEvaluation", "AnswerSubmission", "DimensionScores"]
