"""Facility/Platform model for lab capabilities."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.capability import Capability
    from app.models.lab import Lab
    from app.models.protocol import Protocol


class Facility(Base):
    """Represents a facility or platform within a lab."""

    __tablename__ = "facilities"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    lab_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("labs.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    lab: Mapped["Lab"] = relationship("Lab", back_populates="facilities")
    capabilities: Mapped[list["Capability"]] = relationship(
        "Capability", back_populates="facility", cascade="all, delete-orphan"
    )
    protocols: Mapped[list["Protocol"]] = relationship(
        "Protocol", back_populates="facility", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Facility(id={self.id}, name={self.name})>"
