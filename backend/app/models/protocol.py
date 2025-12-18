"""Protocol/SOP model for facility procedures."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.facility import Facility


class Protocol(Base):
    """Represents a protocol or SOP associated with a facility."""

    __tablename__ = "protocols"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    facility_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("facilities.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    inputs: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    outputs: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    constraints: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    source_document_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("source_documents.id"), nullable=True
    )
    excerpt_offsets: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    facility: Mapped["Facility"] = relationship("Facility", back_populates="protocols")

    def __repr__(self) -> str:
        return f"<Protocol(id={self.id}, title={self.title})>"
