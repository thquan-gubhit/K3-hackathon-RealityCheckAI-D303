"""Redacted, bounded Tutor Agent execution traces."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.document import utc_now


class AgentTrace(Base):
    """One allow-listed tool step in one bounded Tutor Agent run."""

    __tablename__ = "agent_traces"
    __table_args__ = (
        UniqueConstraint(
            "run_id",
            "step_number",
            name="uq_agent_traces_run_step",
        ),
        Index(
            "ix_agent_traces_session_created",
            "session_id",
            "created_at",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    run_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("learning_sessions.id"),
        nullable=False,
    )
    knowledge_unit_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("knowledge_units.id"),
        nullable=False,
    )
    trigger_reason: Mapped[str] = mapped_column(String(64), nullable=False)
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    arguments: Mapped[dict[str, object]] = mapped_column(
        "arguments_json",
        JSON,
        nullable=False,
        default=dict,
    )
    observation: Mapped[dict[str, object]] = mapped_column(
        "observation_json",
        JSON,
        nullable=False,
        default=dict,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )


__all__ = ["AgentTrace"]
