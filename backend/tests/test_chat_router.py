"""Tests for the chat router endpoints."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JobStatus
from app.services.job import get_job_service
from app.models.database import get_db


class TestChatEndpoints:
    """Test suite for chat router endpoints."""

    @pytest.mark.asyncio
    async def test_submit_chat_job(self, db: AsyncSession):
        """Test submitting a chat job."""
        from app.routers.chat import chat
        from app.models.schemas import ChatRequest

        request = ChatRequest(
            message="What are the available capabilities?",
            conversation_id=None,
        )

        response = await chat(request, db=db, background_tasks=None)

        assert response.job_id is not None
        assert response.status == "pending"
        assert "Job submitted" in response.message

    @pytest.mark.asyncio
    async def test_submit_chat_with_conversation_id(self, db: AsyncSession):
        """Test submitting a chat job with an existing conversation."""
        from app.routers.chat import chat
        from app.models.schemas import ChatRequest

        request = ChatRequest(
            message="Continue the previous discussion",
            conversation_id="existing-conv-123",
        )

        response = await chat(request, db=db, background_tasks=None)

        assert response.job_id is not None

    @pytest.mark.asyncio
    async def test_get_job_status_pending(self, db: AsyncSession):
        """Test getting status of a pending job."""
        from app.routers.chat import chat, get_chat_job
        from app.models.schemas import ChatRequest

        # Submit a job
        request = ChatRequest(message="test", conversation_id=None)
        submit_response = await chat(request, db=db, background_tasks=None)
        job_id = submit_response.job_id

        # Get job status
        response = await get_chat_job(job_id, db=db)

        assert response.id == job_id
        assert response.job_type == "chat"
        assert response.status == JobStatus.PENDING
        assert response.progress == 0

    @pytest.mark.asyncio
    async def test_get_nonexistent_job(self, db: AsyncSession):
        """Test getting a nonexistent job returns 404."""
        from app.routers.chat import get_chat_job
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await get_chat_job("nonexistent-job-id", db=db)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_job_response_structure(self, db: AsyncSession):
        """Test that job response has all expected fields."""
        from app.routers.chat import chat, get_chat_job
        from app.models.schemas import ChatRequest

        # Submit a job
        request = ChatRequest(message="test", conversation_id=None)
        submit_response = await chat(request, db=db, background_tasks=None)
        job_id = submit_response.job_id

        response = await get_chat_job(job_id, db=db)

        # Check required fields
        assert hasattr(response, "id")
        assert hasattr(response, "job_type")
        assert hasattr(response, "status")
        assert hasattr(response, "input_data")
        assert hasattr(response, "result")
        assert hasattr(response, "error")
        assert hasattr(response, "progress")
        assert hasattr(response, "progress_message")
        assert hasattr(response, "created_at")
        assert hasattr(response, "started_at")
        assert hasattr(response, "completed_at")

    @pytest.mark.asyncio
    async def test_submission_response_structure(self, db: AsyncSession):
        """Test that submission response has correct structure."""
        from app.routers.chat import chat
        from app.models.schemas import ChatRequest

        request = ChatRequest(message="test", conversation_id=None)
        response = await chat(request, db=db, background_tasks=None)

        assert response.job_id is not None
        assert response.status == "pending"
        assert response.message is not None


class TestChatValidation:
    """Test validation of chat requests."""

    @pytest.mark.asyncio
    async def test_missing_message_field(self, db: AsyncSession):
        """Test that missing message field is rejected."""
        from app.models.schemas import ChatRequest

        # Pydantic will raise a ValidationError for missing required field
        with pytest.raises(Exception):  # ValidationError
            ChatRequest(conversation_id=None)

    @pytest.mark.asyncio
    async def test_empty_message(self, db: AsyncSession):
        """Test that empty message is accepted (might be valid for some use cases)."""
        from app.routers.chat import chat
        from app.models.schemas import ChatRequest

        request = ChatRequest(message="", conversation_id=None)
        response = await chat(request, db=db, background_tasks=None)

        # Should accept it - validation happens downstream
        assert response.job_id is not None

    @pytest.mark.asyncio
    async def test_message_with_special_characters(self, db: AsyncSession):
        """Test that messages with special characters are handled."""
        from app.routers.chat import chat
        from app.models.schemas import ChatRequest

        request = ChatRequest(
            message="Can we test with émojis 🧬 and spëcial çharacters?",
            conversation_id=None,
        )
        response = await chat(request, db=db, background_tasks=None)

        assert response.job_id is not None

    @pytest.mark.asyncio
    async def test_very_long_message(self, db: AsyncSession):
        """Test that very long messages are handled."""
        from app.routers.chat import chat
        from app.models.schemas import ChatRequest

        long_message = "x" * 10000
        request = ChatRequest(message=long_message, conversation_id=None)
        response = await chat(request, db=db, background_tasks=None)

        assert response.job_id is not None
