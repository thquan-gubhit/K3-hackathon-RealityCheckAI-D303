"""Allow-listed, service-backed Tutor Agent tools."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sqlalchemy.orm import Session

from app.models.learning_session import LearningSession
from app.models.question import QuestionType
from app.repositories.knowledge_unit_repository import KnowledgeUnitRepository
from app.repositories.learning_repository import LearningRepository
from app.repositories.question_repository import QuestionRepository
from app.schemas.agent import AgentActionName


class TutorToolError(RuntimeError):
    """Raised when scoped state cannot support a requested tool."""


class TutorTools:
    """Narrow tool registry; no shell, network, or raw database capability."""

    def __init__(
        self,
        session: Session,
        learning_session: LearningSession,
    ) -> None:
        self.session = session
        self.learning_session = learning_session

    def context_snapshot(self) -> dict[str, object]:
        """Return only source-scoped metadata needed for action selection."""

        unit = self._unit()
        repository = LearningRepository(self.session)
        mastery = repository.get_or_create_mastery(
            user_id=self.learning_session.user_id,
            knowledge_unit_id=unit.id,
            initial_score=0.0,
        )
        attempts = repository.list_attempts(self.learning_session.id)
        misconceptions = repository.list_misconceptions(
            user_id=self.learning_session.user_id,
            knowledge_unit_id=unit.id,
            active_only=True,
        )
        return {
            "session_id": self.learning_session.id,
            "knowledge_unit": self.get_current_unit(),
            "mastery": {
                "recall_score": mastery.recall_score,
                "understanding_score": mastery.understanding_score,
                "application_score": mastery.application_score,
                "mastery_score": mastery.mastery_score,
                "status": mastery.status,
            },
            "answer_history": [
                {
                    "question_id": attempt.question_id,
                    "score": attempt.overall_score,
                    "state": attempt.understanding_state,
                }
                for attempt in attempts[-5:]
            ],
            "misconceptions": [
                {
                    "concept": item.concept,
                    "count": item.occurrence_count,
                    "severity": item.severity,
                }
                for item in misconceptions
            ],
        }

    def execute(
        self,
        action: AgentActionName,
        arguments: dict[str, Any],
    ) -> dict[str, object]:
        """Execute exactly one registered action with bounded arguments."""

        registry: dict[AgentActionName, Callable[[], dict[str, object]]] = {
            AgentActionName.GET_CURRENT_UNIT: self.get_current_unit,
            AgentActionName.GET_USER_MASTERY: self.get_user_mastery,
            AgentActionName.GET_ANSWER_HISTORY: self.get_answer_history,
            AgentActionName.GET_DETECTED_MISCONCEPTIONS: (
                self.get_detected_misconceptions
            ),
            AgentActionName.GET_PREREQUISITE_UNITS: self.get_prerequisite_units,
            AgentActionName.GENERATE_SCAFFOLDED_QUESTION: (
                self.generate_scaffolded_question
            ),
            AgentActionName.GIVE_HINT: lambda: self.give_hint(
                str(arguments.get("concept", ""))
            ),
            AgentActionName.GIVE_EXPLANATION: self.give_explanation,
            AgentActionName.FINISH_UNIT: self.finish_unit,
            AgentActionName.ESCALATE_TO_MANUAL_REVIEW: (
                self.escalate_to_manual_review
            ),
        }
        tool = registry.get(action)
        if tool is None:
            raise TutorToolError("The requested tool is not allow-listed.")
        result = tool()
        return {"status": "ok", **result}

    def get_current_unit(self) -> dict[str, object]:
        unit = self._unit()
        return {
            "unit": {
                "id": unit.id,
                "title": unit.title,
                "summary": unit.summary,
                "learning_objectives": list(unit.learning_objectives),
                "key_concepts": list(unit.key_concepts),
                "source_pages": list(unit.source_pages),
            }
        }

    def get_user_mastery(self) -> dict[str, object]:
        mastery = LearningRepository(self.session).get_or_create_mastery(
            user_id=self.learning_session.user_id,
            knowledge_unit_id=self.learning_session.knowledge_unit_id,
            initial_score=0.0,
        )
        return {
            "mastery": {
                "recall_score": mastery.recall_score,
                "understanding_score": mastery.understanding_score,
                "application_score": mastery.application_score,
                "mastery_score": mastery.mastery_score,
                "status": mastery.status,
            }
        }

    def get_answer_history(self) -> dict[str, object]:
        attempts = LearningRepository(self.session).list_attempts(
            self.learning_session.id
        )
        return {
            "attempts": [
                {
                    "question_id": attempt.question_id,
                    "score": attempt.overall_score,
                    "state": attempt.understanding_state,
                }
                for attempt in attempts[-5:]
            ]
        }

    def get_detected_misconceptions(self) -> dict[str, object]:
        records = LearningRepository(self.session).list_misconceptions(
            user_id=self.learning_session.user_id,
            knowledge_unit_id=self.learning_session.knowledge_unit_id,
            active_only=True,
        )
        return {
            "misconceptions": [
                {
                    "concept": record.concept,
                    "count": record.occurrence_count,
                    "severity": record.severity,
                }
                for record in records
            ]
        }

    def get_prerequisite_units(self) -> dict[str, object]:
        unit = self._unit()
        repository = KnowledgeUnitRepository(self.session)
        prerequisites = [
            prerequisite
            for prerequisite_id in unit.prerequisites
            if (prerequisite := repository.get(prerequisite_id)) is not None
        ]
        return {
            "prerequisites": [
                {"id": item.id, "title": item.title}
                for item in prerequisites
            ]
        }

    def generate_scaffolded_question(self) -> dict[str, object]:
        question = QuestionRepository(self.session).first_for_type(
            self.learning_session.knowledge_unit_id,
            QuestionType.RECALL,
        )
        if question is None:
            raise TutorToolError("No source-grounded recall question exists.")
        return {
            "question_id": question.id,
            "question_text": question.question_text,
        }

    def give_hint(self, concept: str) -> dict[str, object]:
        unit = self._unit()
        known = next(
            (
                item
                for item in unit.key_concepts
                if item.casefold() == concept.casefold()
            ),
            unit.key_concepts[0] if unit.key_concepts else unit.title,
        )
        return {
            "hint": (
                f"Focus on how '{known}' connects to the unit's learning "
                "objective; explain the relationship before naming a solution."
            )
        }

    def give_explanation(self) -> dict[str, object]:
        unit = self._unit()
        return {"explanation": unit.summary}

    def finish_unit(self) -> dict[str, object]:
        return {"result": "Finish requested; the workflow must validate it."}

    def escalate_to_manual_review(self) -> dict[str, object]:
        return {"result": "Stopped with an explicit unresolved review state."}

    def _unit(self):
        unit = KnowledgeUnitRepository(self.session).get(
            self.learning_session.knowledge_unit_id
        )
        if unit is None:
            raise TutorToolError("The session Knowledge Unit does not exist.")
        return unit


__all__ = ["TutorToolError", "TutorTools"]
