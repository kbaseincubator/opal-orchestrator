"""Conversation model for chat history persistence."""

from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import JSON, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class Conversation(Base):
    """Represents a chat conversation session."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    messages: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    plan: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    sources: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, title={self.title})>"

    def get_preview(self) -> str:
        """Get a preview of the conversation from the first user message."""
        for msg in self.messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                return content[:100] + "..." if len(content) > 100 else content
        return "New conversation"
