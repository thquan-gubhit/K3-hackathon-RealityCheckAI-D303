"""API contracts for sessions, attempts, mastery, and progress."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.learning_session import LearningSessionStatus
from app.models.mastery import MasteryStatus
from app.schemas.evaluation import AnswerEvaluation
from app.schemas.question import QuestionPublic


class LearningSessionCreate(BaseModel):
    """Start one local-user session on a ready document/KU."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    user_id: str = Field(default="local-user", min_length=1, max_length=100)
    document_id: str = Field(min_length=1, max_length=100)
    knowledge_unit_id: str | None = Field(default=None, max_length=100)


class LearningSessionRead(BaseModel):
    """Persisted session state."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    document_id: str
    knowledge_unit_id: str
    current_question_id: str | None
    started_at: datetime
    completed_at: datetime | None
    status: LearningSessionStatus
    main_question_count: int = Field(ge=0)
    remediation_question_count: int = Field(ge=0)


class MasteryRead(BaseModel):
    """Current dimension and evidence state for one user/KU."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    knowledge_unit_id: str
    recall_score: float = Field(ge=0.0, le=1.0)
    understanding_score: float = Field(ge=0.0, le=1.0)
    application_score: float = Field(ge=0.0, le=1.0)
    mastery_score: float = Field(ge=0.0, le=1.0)
    status: MasteryStatus
    question_evidence_count: int = Field(ge=0)
    has_application_evidence: bool
    last_updated: datetime


class MisconceptionRead(BaseModel):
    """Aggregated misconception exposed in progress feedback."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    knowledge_unit_id: str
    concept: str
    description: str
    occurrence_count: int = Field(ge=1)
    severity: str
    resolved: bool
    last_detected_at: datetime


class AnswerAttemptRead(BaseModel):
    """Safe persisted answer evidence."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    session_id: str
    question_id: str
    user_answer: str
    overall_score: float = Field(ge=0.0, le=1.0)
    attempt_number: int = Field(ge=1)
    evidence_weight: float = Field(gt=0.0, le=1.0)
    understanding_state: str
    previous_mastery: float = Field(ge=0.0, le=1.0)
    new_mastery: float = Field(ge=0.0, le=1.0)
    created_at: datetime


class NextQuestionResponse(BaseModel):
    """Deterministically selected next learner activity."""

    session: LearningSessionRead
    question: QuestionPublic | None
    route_reason: str
    next_action: str


class AnswerResultResponse(BaseModel):
    """Atomic evaluation and mastery update result."""

    attempt: AnswerAttemptRead
    evaluation: AnswerEvaluation
    mastery: MasteryRead
    misconceptions: list[MisconceptionRead]
    next_action: str


class ProgressUnitResponse(BaseModel):
    """Knowledge Unit metadata plus current learner progress."""

    knowledge_unit_id: str
    title: str
    position: int
    mastery: MasteryRead
    answered_questions: int = Field(ge=0)
    active_misconceptions: list[MisconceptionRead]


class UserProgressResponse(BaseModel):
    """Aggregate local-user progress across persisted Knowledge Units."""

    user_id: str
    knowledge_units: list[ProgressUnitResponse]
    recommended_next_unit_id: str | None


__all__ = [
    "AnswerAttemptRead",
    "AnswerResultResponse",
    "LearningSessionCreate",
    "LearningSessionRead",
    "MasteryRead",
    "MisconceptionRead",
    "NextQuestionResponse",
    "ProgressUnitResponse",
    "UserProgressResponse",
]
