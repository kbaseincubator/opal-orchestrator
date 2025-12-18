"""Lab model for OPAL member institutions."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base

if TYPE_CHECKING:
    from app.models.facility import Facility
    from app.models.resource import Resource


class Lab(Base):
    """Represents an OPAL member laboratory or institution."""

    __tablename__ = "labs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    institution: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contacts: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    urls: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    facilities: Mapped[list["Facility"]] = relationship(
        "Facility", back_populates="lab", cascade="all, delete-orphan"
    )
    resources: Mapped[list["Resource"]] = relationship(
        "Resource", back_populates="lab", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Lab(id={self.id}, name={self.name}, institution={self.institution})>"
