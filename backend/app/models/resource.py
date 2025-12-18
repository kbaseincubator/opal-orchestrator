"""Resource model for lab resources (strains, libraries, instruments, etc.)."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.lab import Lab


class ResourceType(str, Enum):
    """Types of resources available at labs."""

    STRAIN = "strain"
    LIBRARY = "library"
    INSTRUMENT = "instrument"
    ASSAY = "assay"
    DATASET = "dataset"
    OTHER = "other"


class Resource(Base):
    """Represents a resource available at a lab."""

    __tablename__ = "resources"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    lab_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("labs.id"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    access_constraints: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)
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
    lab: Mapped["Lab"] = relationship("Lab", back_populates="resources")

    def __repr__(self) -> str:
        return f"<Resource(id={self.id}, type={self.type}, name={self.name})>"
