"""Service for managing async jobs."""

from datetime import datetime, timezone
from typing import Optional
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job, JobStatus

logger = logging.getLogger(__name__)


class JobService:
    """Service for managing job lifecycle."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(
        self,
        job_type: str,
        input_data: dict,
    ) -> Job:
        """Create a new job."""
        job = Job(
            job_type=job_type,
            status=JobStatus.PENDING,
            input_data=input_data,
        )
        self.db.add(job)
        await self.db.flush()
        await self.db.commit()
        logger.info(f"Created job {job.id} of type {job_type}")
        return job

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        result = await self.db.execute(
            select(Job).where(Job.id == job_id)
        )
        return result.scalar_one_or_none()

    async def start_job(self, job_id: str) -> None:
        """Mark job as processing."""
        job = await self.get_job(job_id)
        if job:
            job.status = JobStatus.PROCESSING
            job.started_at = datetime.now(timezone.utc)
            await self.db.commit()
            logger.info(f"Started job {job_id}")

    async def complete_job(
        self,
        job_id: str,
        result: dict,
    ) -> None:
        """Mark job as completed with result."""
        job = await self.get_job(job_id)
        if job:
            job.status = JobStatus.COMPLETED
            job.result = result
            job.completed_at = datetime.now(timezone.utc)
            job.progress = 100
            await self.db.commit()
            logger.info(f"Completed job {job_id}")

    async def fail_job(
        self,
        job_id: str,
        error: str,
    ) -> None:
        """Mark job as failed with error message."""
        job = await self.get_job(job_id)
        if job:
            job.status = JobStatus.FAILED
            job.error = error
            job.completed_at = datetime.now(timezone.utc)
            await self.db.commit()
            logger.error(f"Job {job_id} failed: {error}")

    async def update_progress(
        self,
        job_id: str,
        progress: int,
        message: Optional[str] = None,
    ) -> None:
        """Update job progress."""
        job = await self.get_job(job_id)
        if job:
            job.progress = progress
            if message:
                job.progress_message = message
            await self.db.commit()


def get_job_service(db: AsyncSession) -> JobService:
    """Get a job service instance."""
    return JobService(db)
