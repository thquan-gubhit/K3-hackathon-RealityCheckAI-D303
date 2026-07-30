"""SQLAlchemy model modules.

Models are introduced with their owning product phases. Import them here so
``app.database.init_db`` can register all metadata in one predictable place.
"""

from app.models.agent_trace import AgentTrace
from app.models.answer import AnswerAttempt
from app.models.document import Document, DocumentPage, DocumentStatus
from app.models.knowledge_unit import KnowledgeUnit
from app.models.learning_session import LearningSession, LearningSessionStatus
from app.models.mastery import MasteryState, MasteryStatus, Misconception
from app.models.question import (
    Question,
    QuestionDifficulty,
    QuestionType,
    QuestionValidationStatus,
)

__all__ = [
    "AgentTrace",
    "AnswerAttempt",
    "Document",
    "DocumentPage",
    "DocumentStatus",
    "KnowledgeUnit",
    "LearningSession",
    "LearningSessionStatus",
    "MasteryState",
    "MasteryStatus",
    "Misconception",
    "Question",
    "QuestionDifficulty",
    "QuestionType",
    "QuestionValidationStatus",
]
