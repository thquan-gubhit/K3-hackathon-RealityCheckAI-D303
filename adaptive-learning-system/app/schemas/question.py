"""Pydantic contracts for immutable, source-grounded questions and rubrics."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import uuid4

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)

from app.models.question import (
    QuestionDifficulty,
    QuestionType,
    QuestionValidationStatus,
)


NonEmptyText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]
MANDATORY_QUESTION_TYPES = (
    QuestionType.RECALL,
    QuestionType.EXPLAIN,
    QuestionType.APPLY,
)


def _unique_strings(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        normalized = value.strip()
        if not normalized:
            raise ValueError("list entries must be non-empty")
        key = normalized.casefold()
        if key not in seen:
            seen.add(key)
            result.append(normalized)
    return result


class RubricPoint(BaseModel):
    """One observable answer point and its normalized contribution."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    point: NonEmptyText
    weight: float = Field(gt=0.0, le=1.0)


class DimensionWeights(BaseModel):
    """Weights for deterministic recomputation of the overall score."""

    model_config = ConfigDict(extra="forbid")

    correctness: float = Field(ge=0.0, le=1.0)
    coverage: float = Field(ge=0.0, le=1.0)
    reasoning: float = Field(ge=0.0, le=1.0)
    application: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def weights_sum_to_one(self) -> "DimensionWeights":
        total = (
            self.correctness
            + self.coverage
            + self.reasoning
            + self.application
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError("dimension weights must sum to 1.0")
        return self


class QuestionRubric(BaseModel):
    """Immutable rubric generated and persisted before learner exposure."""

    model_config = ConfigDict(extra="forbid")

    required_points: list[RubricPoint] = Field(min_length=1, max_length=20)
    optional_points: list[RubricPoint] = Field(default_factory=list, max_length=20)
    acceptable_alternatives: list[str] = Field(default_factory=list, max_length=50)
    misconceptions: list[str] = Field(default_factory=list, max_length=50)
    dimension_weights: DimensionWeights

    @field_validator("acceptable_alternatives", "misconceptions")
    @classmethod
    def normalize_lists(cls, values: list[str]) -> list[str]:
        return _unique_strings(values)

    @model_validator(mode="after")
    def point_weights_sum_to_one(self) -> "QuestionRubric":
        total = sum(
            point.weight
            for point in [*self.required_points, *self.optional_points]
        )
        if abs(total - 1.0) > 1e-6:
            raise ValueError("rubric point weights must sum to 1.0")
        return self


class QuestionContent(BaseModel):
    """Question content shared by LLM candidates and persistence inputs."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    learning_objective: str = Field(min_length=1, max_length=2_000)
    question_type: QuestionType
    difficulty: QuestionDifficulty = QuestionDifficulty.MEDIUM
    question_text: str = Field(min_length=5, max_length=10_000)
    reference_answer: str = Field(min_length=1, max_length=20_000)
    rubric: QuestionRubric
    source_pages: list[int] = Field(min_length=1, max_length=1_000)


    @field_validator("source_pages")
    @classmethod
    def normalize_pages(cls, pages: list[int]) -> list[int]:
        if any(page < 1 for page in pages):
            raise ValueError("source pages must be positive")
        return sorted(set(pages))


class QuestionCandidate(QuestionContent):
    """LLM output plus semantic validation signals."""

    candidate_id: str | None = Field(default=None, min_length=1, max_length=100)
    source_grounded: bool
    objective_aligned: bool
    answer_leak: bool = False
    ambiguous: bool = False
    requires_external_knowledge: bool = False


class QuestionBatch(BaseModel):
    """Bounded structured question-generation response."""

    model_config = ConfigDict(extra="forbid")

    candidates: list[QuestionCandidate] = Field(
        min_length=1,
        max_length=30,
        validation_alias=AliasChoices("candidates", "questions"),
    )


class QuestionCreate(QuestionContent):
    """Validated accepted question ready for persistence."""

    id: str = Field(default_factory=lambda: str(uuid4()), max_length=100)
    knowledge_unit_id: str = Field(min_length=1, max_length=100)
    validation_status: QuestionValidationStatus = (
        QuestionValidationStatus.ACCEPTED
    )
    rubric_version: int = Field(default=1, ge=1)


class QuestionPublic(BaseModel):
    """Learner-safe question shape; answer and rubric are intentionally absent."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    knowledge_unit_id: str
    learning_objective: str
    question_type: QuestionType
    difficulty: QuestionDifficulty
    question_text: str
    source_pages: list[int]
    validation_status: QuestionValidationStatus
    created_at: datetime


class QuestionInternalRead(QuestionPublic):
    """Internal/admin shape used by tests and service boundaries."""

    reference_answer: str
    rubric: QuestionRubric
    rubric_version: int


class QuestionGenerationResponse(BaseModel):
    """Idempotent accepted question set returned without answer leakage."""

    knowledge_unit_id: str
    questions: list[QuestionPublic]


__all__ = [
    "DimensionWeights",
    "MANDATORY_QUESTION_TYPES",
    "QuestionBatch",
    "QuestionCandidate",
    "QuestionContent",
    "QuestionCreate",
    "QuestionGenerationResponse",
    "QuestionInternalRead",
    "QuestionPublic",
    "QuestionRubric",
    "RubricPoint",
]
