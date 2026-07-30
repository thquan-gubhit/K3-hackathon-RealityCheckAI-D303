"""Persistence operations for a document's validated Knowledge Map."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.knowledge_unit import KnowledgeUnit
from app.schemas.knowledge_unit import KnowledgeUnitCreate, KnowledgeUnitStatus


class KnowledgeUnitRepository:
    """Transaction-aware repository; callers own commit and rollback."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def replace_for_document(
        self,
        document_id: str,
        units: Sequence[KnowledgeUnitCreate],
    ) -> list[KnowledgeUnit]:
        """Atomically stage replacement rows and flush without committing."""

        if not document_id.strip():
            raise ValueError("document_id must be non-empty")
        if not units:
            raise ValueError("a valid Knowledge Map must contain at least one unit")
        if any(unit.document_id != document_id for unit in units):
            raise ValueError("every Knowledge Unit must belong to document_id")

        ids = [unit.id for unit in units]
        if len(ids) != len(set(ids)):
            raise ValueError("Knowledge Unit IDs must be unique")
        positions = sorted(unit.position for unit in units)
        if positions != list(range(1, len(units) + 1)):
            raise ValueError("Knowledge Unit positions must be contiguous from 1")
        if any(unit.status is not KnowledgeUnitStatus.VALID for unit in units):
            raise ValueError("only validated Knowledge Units may be persisted")

        self._session.execute(
            delete(KnowledgeUnit).where(KnowledgeUnit.document_id == document_id)
        )
        records = [
            KnowledgeUnit(
                id=unit.id,
                document_id=unit.document_id,
                position=unit.position,
                title=unit.title,
                summary=unit.summary,
                learning_objectives=list(unit.learning_objectives),
                key_concepts=list(unit.key_concepts),
                concept_relations=[
                    relation.model_dump() for relation in unit.concept_relations
                ],
                prerequisites=list(unit.prerequisites),
                common_misconceptions=list(unit.common_misconceptions),
                source_pages=list(unit.source_pages),
                estimated_reading_minutes=unit.estimated_reading_minutes,
                status=unit.status.value,
            )
            for unit in units
        ]
        self._session.add_all(records)
        self._session.flush()
        return records

    def list_for_document(
        self,
        document_id: str,
        *,
        status: KnowledgeUnitStatus | str = KnowledgeUnitStatus.VALID,
    ) -> list[KnowledgeUnit]:
        """Return a stable, ordered Knowledge Map for one document."""

        status_value = status.value if isinstance(status, KnowledgeUnitStatus) else status
        statement = (
            select(KnowledgeUnit)
            .where(
                KnowledgeUnit.document_id == document_id,
                KnowledgeUnit.status == status_value,
            )
            .order_by(KnowledgeUnit.position, KnowledgeUnit.id)
        )
        return list(self._session.scalars(statement).all())

    def get(self, unit_id: str) -> KnowledgeUnit | None:
        """Return one Knowledge Unit by identifier."""

        return self._session.get(KnowledgeUnit, unit_id)

    def list_all(self) -> list[KnowledgeUnit]:
        """Return all valid units in stable document/position order."""

        statement = (
            select(KnowledgeUnit)
            .where(KnowledgeUnit.status == KnowledgeUnitStatus.VALID.value)
            .order_by(
                KnowledgeUnit.document_id,
                KnowledgeUnit.position,
                KnowledgeUnit.id,
            )
        )
        return list(self._session.scalars(statement).all())


__all__ = ["KnowledgeUnitRepository"]
