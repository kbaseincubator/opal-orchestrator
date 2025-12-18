"""Source document and chunk models for RAG."""

from datetime import datetime
from enum import Enum
from typing import Optional
import uuid

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class SourceType(str, Enum):
    """Types of source documents."""

    PDF = "pdf"
    HTML = "html"
    DOC = "doc"
    YAML = "yaml"
    MANUAL = "manual"


class SourceDocument(Base):
    """Represents an ingested source document."""

    __tablename__ = "source_documents"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    url_or_path: Mapped[str] = mapped_column(String(2000), nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)

    # Relationships
    chunks: Mapped[list["SourceChunk"]] = relationship(
        "SourceChunk", back_populates="source_document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SourceDocument(id={self.id}, title={self.title}, type={self.type})>"


class SourceChunk(Base):
    """Represents a chunk of text from a source document for embedding."""

    __tablename__ = "source_chunks"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    source_document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("source_documents.id"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON, nullable=True)
    chunk_index: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    source_document: Mapped["SourceDocument"] = relationship(
        "SourceDocument", back_populates="chunks"
    )

    def __repr__(self) -> str:
        return f"<SourceChunk(id={self.id}, doc_id={self.source_document_id})>"
