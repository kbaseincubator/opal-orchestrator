"""Integration tests for the job queue system."""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import JobStatus
from app.services.job import JobService
from app.models.database import async_session_maker


@pytest.mark.asyncio
class TestJobIntegration:
    """Integration tests for job queue functionality."""

    async def test_job_creation_and_retrieval(self, db: AsyncSession):
        """Test creating and retrieving a job."""
        job_service = JobService(db)

        # Create job
        job = await job_service.create_job(
            job_type="chat",
            input_data={"message": "test message"},
        )

        assert job.id is not None
        job_id = job.id

        # Retrieve job
        retrieved = await job_service.get_job(job_id)
        assert retrieved is not None
        assert retrieved.id == job_id
        assert retrieved.job_type == "chat"
        assert retrieved.status == JobStatus.PENDING

    async def test_job_state_transitions(self, db: AsyncSession):
        """Test valid job state transitions."""
        job_service = JobService(db)

        # Create job
        job = await job_service.create_job("chat", {})
        assert job.status == JobStatus.PENDING

        # Start job
        await job_service.start_job(job.id)
        job = await job_service.get_job(job.id)
        assert job.status == JobStatus.PROCESSING
        assert job.started_at is not None

        # Progress updates while processing
        await job_service.update_progress(job.id, 25, "Processing...")
        job = await job_service.get_job(job.id)
        assert job.progress == 25

        await job_service.update_progress(job.id, 75, "Almost done")
        job = await job_service.get_job(job.id)
        assert job.progress == 75

        # Complete job
        result = {"message": "Done!", "plan": None}
        await job_service.complete_job(job.id, result)
        job = await job_service.get_job(job.id)
        assert job.status == JobStatus.COMPLETED
        assert job.result == result
        assert job.progress == 100
        assert job.completed_at is not None

    async def test_job_failure_handling(self, db: AsyncSession):
        """Test handling job failures."""
        job_service = JobService(db)

        # Create and start job
        job = await job_service.create_job("chat", {})
        await job_service.start_job(job.id)

        # Simulate failure
        error_msg = "LLM refused to process request"
        await job_service.fail_job(job.id, error_msg)

        job = await job_service.get_job(job.id)
        assert job.status == JobStatus.FAILED
        assert job.error == error_msg
        assert job.completed_at is not None

    async def test_multiple_concurrent_jobs(self, db: AsyncSession):
        """Test handling multiple jobs concurrently."""
        job_service = JobService(db)

        # Create multiple jobs
        job_ids = []
        for i in range(5):
            job = await job_service.create_job(
                "chat",
                {"message": f"Message {i}"},
            )
            job_ids.append(job.id)

        # Verify all jobs were created
        assert len(job_ids) == 5

        # Retrieve all jobs
        jobs = []
        for job_id in job_ids:
            job = await job_service.get_job(job_id)
            assert job is not None
            jobs.append(job)

        # Verify all are pending
        assert all(j.status == JobStatus.PENDING for j in jobs)

    async def test_job_result_preservation(self, db: AsyncSession):
        """Test that complex result objects are preserved."""
        job_service = JobService(db)

        # Create a complex result
        complex_result = {
            "message": "Here's what I found",
            "plan": {
                "steps": [
                    {"id": "S1", "objective": "Do something"},
                    {"id": "S2", "objective": "Do something else"},
                ],
                "dependencies": {"S2": ["S1"]},
            },
            "sources": [
                {"id": "src1", "title": "Paper 1"},
                {"id": "src2", "title": "Paper 2"},
            ],
            "metadata": {
                "version": "1.0",
                "timestamp": "2024-01-01T00:00:00Z",
                "tags": ["urgent", "research"],
            },
        }

        # Create and complete job with complex result
        job = await job_service.create_job("chat", {})
        await job_service.complete_job(job.id, complex_result)

        # Retrieve and verify result is preserved
        completed_job = await job_service.get_job(job.id)
        assert completed_job.result == complex_result
        assert completed_job.result["plan"]["steps"][0]["id"] == "S1"
        assert completed_job.result["metadata"]["tags"] == ["urgent", "research"]

    async def test_job_input_data_preservation(self, db: AsyncSession):
        """Test that input data is preserved."""
        job_service = JobService(db)

        input_data = {
            "message": "Can you analyze this?",
            "conversation_id": "conv-123",
            "metadata": {"user_id": "user-456"},
        }

        job = await job_service.create_job("chat", input_data)
        retrieved = await job_service.get_job(job.id)

        assert retrieved.input_data == input_data

    async def test_job_timestamps(self, db: AsyncSession):
        """Test that job timestamps are correctly recorded."""
        from datetime import timezone

        job_service = JobService(db)

        # Create job
        job = await job_service.create_job("chat", {})
        created_at = job.created_at
        assert created_at is not None
        assert job.started_at is None
        assert job.completed_at is None

        # Make created_at timezone-aware for comparison
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        # Start job
        await job_service.start_job(job.id)
        job = await job_service.get_job(job.id)
        assert job.started_at is not None
        assert job.started_at >= created_at

        # Complete job
        await job_service.complete_job(job.id, {})
        job = await job_service.get_job(job.id)
        assert job.completed_at is not None
        assert job.completed_at >= job.started_at

    async def test_progress_message_optional(self, db: AsyncSession):
        """Test that progress message is optional."""
        job_service = JobService(db)

        job = await job_service.create_job("chat", {})

        # Update progress without message
        await job_service.update_progress(job.id, 50)
        job = await job_service.get_job(job.id)
        assert job.progress == 50
        assert job.progress_message is None

        # Update with message
        await job_service.update_progress(job.id, 75, "Processing step 2")
        job = await job_service.get_job(job.id)
        assert job.progress == 75
        assert job.progress_message == "Processing step 2"
