"""Tests for the job service."""

import pytest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job, JobStatus
from app.services.job import JobService


@pytest.fixture
async def job_service(db: AsyncSession) -> JobService:
    """Fixture to provide a JobService instance."""
    return JobService(db)


class TestJobService:
    """Test suite for JobService."""

    async def test_create_job(self, job_service: JobService):
        """Test creating a new job."""
        input_data = {"message": "test message", "conversation_id": "conv123"}
        job = await job_service.create_job("chat", input_data)

        assert job is not None
        assert job.id is not None
        assert job.job_type == "chat"
        assert job.status == JobStatus.PENDING
        assert job.input_data == input_data
        assert job.result is None
        assert job.error is None
        assert job.progress == 0

    async def test_get_job(self, job_service: JobService):
        """Test retrieving a job by ID."""
        input_data = {"message": "test"}
        created_job = await job_service.create_job("chat", input_data)

        retrieved_job = await job_service.get_job(created_job.id)

        assert retrieved_job is not None
        assert retrieved_job.id == created_job.id
        assert retrieved_job.job_type == "chat"

    async def test_get_nonexistent_job(self, job_service: JobService):
        """Test retrieving a nonexistent job returns None."""
        job = await job_service.get_job("nonexistent-id")
        assert job is None

    async def test_start_job(self, job_service: JobService):
        """Test marking a job as started."""
        job = await job_service.create_job("chat", {})
        await job_service.start_job(job.id)

        started_job = await job_service.get_job(job.id)
        assert started_job.status == JobStatus.PROCESSING
        assert started_job.started_at is not None

    async def test_complete_job(self, job_service: JobService):
        """Test marking a job as completed with result."""
        job = await job_service.create_job("chat", {})
        result = {"message": "response", "plan": None}

        await job_service.complete_job(job.id, result)

        completed_job = await job_service.get_job(job.id)
        assert completed_job.status == JobStatus.COMPLETED
        assert completed_job.result == result
        assert completed_job.completed_at is not None
        assert completed_job.progress == 100

    async def test_fail_job(self, job_service: JobService):
        """Test marking a job as failed with error."""
        job = await job_service.create_job("chat", {})
        error_msg = "Something went wrong"

        await job_service.fail_job(job.id, error_msg)

        failed_job = await job_service.get_job(job.id)
        assert failed_job.status == JobStatus.FAILED
        assert failed_job.error == error_msg
        assert failed_job.completed_at is not None

    async def test_update_progress(self, job_service: JobService):
        """Test updating job progress."""
        job = await job_service.create_job("chat", {})

        await job_service.update_progress(job.id, 50, "Half way done")

        progress_job = await job_service.get_job(job.id)
        assert progress_job.progress == 50
        assert progress_job.progress_message == "Half way done"

    async def test_update_progress_without_message(self, job_service: JobService):
        """Test updating progress without a message."""
        job = await job_service.create_job("chat", {})

        await job_service.update_progress(job.id, 75)

        progress_job = await job_service.get_job(job.id)
        assert progress_job.progress == 75
        assert progress_job.progress_message is None

    async def test_job_lifecycle(self, job_service: JobService):
        """Test the complete job lifecycle."""
        # Create
        job = await job_service.create_job("chat", {"message": "test"})
        assert job.status == JobStatus.PENDING

        # Start
        await job_service.start_job(job.id)
        job = await job_service.get_job(job.id)
        assert job.status == JobStatus.PROCESSING

        # Progress
        await job_service.update_progress(job.id, 50)
        job = await job_service.get_job(job.id)
        assert job.progress == 50

        # Complete
        result = {"message": "done"}
        await job_service.complete_job(job.id, result)
        job = await job_service.get_job(job.id)
        assert job.status == JobStatus.COMPLETED
        assert job.result == result
        assert job.progress == 100
