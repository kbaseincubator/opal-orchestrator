"""Conversations API router for chat history management."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation
from app.models.database import get_db

router = APIRouter(prefix="/conversations", tags=["conversations"])


class ConversationSummary(BaseModel):
    """Summary of a conversation for listing."""
    id: str
    title: Optional[str]
    preview: str
    message_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    """Full conversation with messages."""
    id: str
    title: Optional[str]
    messages: list
    plan: Optional[dict]
    sources: list
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationUpdate(BaseModel):
    """Request to update a conversation."""
    title: Optional[str] = None


@router.get("", response_model=list[ConversationSummary])
async def list_conversations(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[ConversationSummary]:
    """List all conversations, newest first.

    Args:
        skip: Number of conversations to skip
        limit: Maximum number of conversations to return
        db: Database session

    Returns:
        List of conversation summaries
    """
    result = await db.execute(
        select(Conversation)
        .order_by(desc(Conversation.updated_at))
        .offset(skip)
        .limit(limit)
    )
    conversations = result.scalars().all()

    return [
        ConversationSummary(
            id=conv.id,
            title=conv.title,
            preview=conv.get_preview(),
            message_count=len(conv.messages),
            created_at=conv.created_at,
            updated_at=conv.updated_at,
        )
        for conv in conversations
    ]


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
) -> ConversationDetail:
    """Get a specific conversation with all messages.

    Args:
        conversation_id: ID of the conversation
        db: Database session

    Returns:
        Full conversation details
    """
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        messages=conversation.messages,
        plan=conversation.plan,
        sources=conversation.sources or [],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@router.patch("/{conversation_id}", response_model=ConversationDetail)
async def update_conversation(
    conversation_id: str,
    update: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
) -> ConversationDetail:
    """Update a conversation (e.g., rename title).

    Args:
        conversation_id: ID of the conversation
        update: Fields to update
        db: Database session

    Returns:
        Updated conversation
    """
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if update.title is not None:
        conversation.title = update.title

    await db.commit()
    await db.refresh(conversation)

    return ConversationDetail(
        id=conversation.id,
        title=conversation.title,
        messages=conversation.messages,
        plan=conversation.plan,
        sources=conversation.sources or [],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete a conversation.

    Args:
        conversation_id: ID of the conversation to delete
        db: Database session

    Returns:
        Confirmation message
    """
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    await db.delete(conversation)
    await db.commit()

    return {"message": "Conversation deleted", "id": conversation_id}
