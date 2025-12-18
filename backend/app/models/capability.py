"""Capability model for facility capabilities."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.facility import Facility


class Capability(Base):
    """Represents a specific capability offered by a facility."""

    __tablename__ = "capabilities"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    facility_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("facilities.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    modalities: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    throughput: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sample_requirements: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    constraints: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    typical_outputs: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    readiness_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    source_document_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("source_documents.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    facility: Mapped["Facility"] = relationship("Facility", back_populates="capabilities")

    def __repr__(self) -> str:
        return f"<Capability(id={self.id}, name={self.name})>"
