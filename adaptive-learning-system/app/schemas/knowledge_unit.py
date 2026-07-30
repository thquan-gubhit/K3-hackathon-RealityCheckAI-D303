"""Pydantic contracts for source-grounded Knowledge Units."""

from __future__ import annotations

from enum import Enum
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


NonEmptyText = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1),
]


class KnowledgeUnitStatus(str, Enum):
    """Persistable Knowledge Unit states for the Phase 2 map."""

    VALID = "valid"


def _unique_strings(values: list[str]) -> list[str]:
    """Strip and case-insensitively deduplicate a list while preserving order."""

    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = value.strip()
        if not item:
            raise ValueError("list entries must be non-empty strings")
        key = item.casefold()
        if key not in seen:
            normalized.append(item)
            seen.add(key)
    return normalized


class ConceptRelation(BaseModel):
    """A directed, source-grounded relation between two concepts."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source: NonEmptyText
    relation: NonEmptyText
    target: NonEmptyText

    @model_validator(mode="after")
    def reject_self_relation(self) -> "ConceptRelation":
        if self.source.casefold() == self.target.casefold():
            raise ValueError("a concept relation cannot point to itself")
        return self


class KnowledgeUnitContent(BaseModel):
    """Fields shared by LLM candidates and persisted Knowledge Units.

    Configurable size limits intentionally live in the deterministic rule
    engine. This schema validates shape and safe absolute bounds so a candidate
    that needs splitting or merging can still be parsed and diagnosed.
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )

    title: str = Field(min_length=1, max_length=500)
    summary: str = Field(min_length=1, max_length=10_000)
    learning_objectives: list[str] = Field(min_length=1, max_length=20)
    key_concepts: list[str] = Field(default_factory=list, max_length=50)
    concept_relations: list[ConceptRelation] = Field(
        default_factory=list,
        max_length=100,
    )
    prerequisites: list[str] = Field(default_factory=list, max_length=50)
    common_misconceptions: list[str] = Field(default_factory=list, max_length=50)
    source_pages: list[int] = Field(min_length=1, max_length=10_000)
    estimated_reading_minutes: int = Field(ge=1, le=1_440)

    @field_validator(
        "learning_objectives",
        "key_concepts",
        "prerequisites",
        "common_misconceptions",
    )
    @classmethod
    def normalize_string_lists(cls, values: list[str]) -> list[str]:
        return _unique_strings(values)

    @field_validator("source_pages")
    @classmethod
    def normalize_source_pages(cls, values: list[int]) -> list[int]:
        if any(page < 1 for page in values):
            raise ValueError("source pages must be positive integers")
        return sorted(set(values))

    @field_validator("concept_relations")
    @classmethod
    def deduplicate_relations(
        cls,
        values: list[ConceptRelation],
    ) -> list[ConceptRelation]:
        result: list[ConceptRelation] = []
        seen: set[tuple[str, str, str]] = set()
        for relation in values:
            key = (
                relation.source.casefold(),
                relation.relation.casefold(),
                relation.target.casefold(),
            )
            if key not in seen:
                result.append(relation)
                seen.add(key)
        return result


class KnowledgeUnitCandidate(KnowledgeUnitContent):
    """LLM-produced KU metadata plus semantic signals used by deterministic rules."""

    candidate_id: str | None = Field(default=None, min_length=1, max_length=100)
    has_independent_objective: bool = True
    is_only_example: bool = False
    can_generate_independent_question: bool = True


class KnowledgeUnitBatch(BaseModel):
    """Bounded container returned by Knowledge Unit generation/refinement calls."""

    model_config = ConfigDict(extra="forbid")

    candidates: list[KnowledgeUnitCandidate] = Field(
        min_length=1,
        max_length=20,
        validation_alias=AliasChoices("candidates", "units"),
    )

    @model_validator(mode="after")
    def candidate_ids_are_unique(self) -> "KnowledgeUnitBatch":
        ids = [
            candidate.candidate_id.casefold()
            for candidate in self.candidates
            if candidate.candidate_id is not None
        ]
        if len(ids) != len(set(ids)):
            raise ValueError("candidate_id values must be unique within a batch")
        return self


class KnowledgeUnitCreate(KnowledgeUnitContent):
    """Validated input for atomically replacing a document's Knowledge Map."""

    id: str = Field(
        default_factory=lambda: str(uuid4()),
        min_length=1,
        max_length=100,
    )
    document_id: str = Field(min_length=1, max_length=100)
    position: int = Field(ge=1)
    status: KnowledgeUnitStatus = KnowledgeUnitStatus.VALID

    @model_validator(mode="after")
    def reject_self_prerequisite(self) -> "KnowledgeUnitCreate":
        if self.id.casefold() in {
            prerequisite.casefold() for prerequisite in self.prerequisites
        }:
            raise ValueError("a Knowledge Unit cannot require itself")
        return self


class KnowledgeUnitRead(KnowledgeUnitCreate):
    """Public response shape; it contains metadata but never full source text."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")


# Clear transport-facing alias for API modules.
KnowledgeUnitResponse = KnowledgeUnitRead


__all__ = [
    "ConceptRelation",
    "KnowledgeUnitBatch",
    "KnowledgeUnitCandidate",
    "KnowledgeUnitContent",
    "KnowledgeUnitCreate",
    "KnowledgeUnitRead",
    "KnowledgeUnitResponse",
    "KnowledgeUnitStatus",
]
