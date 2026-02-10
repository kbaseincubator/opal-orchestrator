"""Chat API router."""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import ChatRequest, ChatResponse, JobSubmissionResponse, JobResponse
from app.services.chat import get_chat_service
from app.services.job import get_job_service
from app.services.llm import LLMRefusalError
import logging

router = APIRouter(prefix="/chat", tags=["chat"])

logger = logging.getLogger(__name__)


def _serialize_for_json(obj: any) -> any:
    """Recursively serialize objects to JSON-compatible types."""
    from datetime import datetime

    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_serialize_for_json(item) for item in obj]
    else:
        return obj


async def process_chat_job(
    job_id: str,
    message: str,
    conversation_id: str,
    db_url: str,
):
    """Background task to process a chat job."""
    from app.models.database import async_session_maker

    try:
        async with async_session_maker() as db:
            job_service = get_job_service(db)
            chat_service = get_chat_service(db)

            await job_service.start_job(job_id)

            response = await chat_service.chat(
                message=message,
                conversation_id=conversation_id,
            )

            # Convert ChatResponse to dict for storage
            result_dict = response.dict() if hasattr(response, 'dict') else response.__dict__
            # Serialize any non-JSON-serializable objects (like datetime)
            result_dict = _serialize_for_json(result_dict)
            await job_service.complete_job(job_id, result_dict)

    except LLMRefusalError as e:
        async with async_session_maker() as db:
            job_service = get_job_service(db)
            await job_service.fail_job(job_id, str(e))
    except Exception as e:
        logger.error(f"Error processing chat job {job_id}: {e}", exc_info=True)
        async with async_session_maker() as db:
            job_service = get_job_service(db)
            await job_service.fail_job(job_id, str(e))


@router.post("", response_model=JobSubmissionResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = None,
) -> JobSubmissionResponse:
    """Submit a chat message for processing.

    This endpoint submits a chat request and returns immediately with a job ID.
    The actual processing happens in the background. Use the /chat/{job_id}
    endpoint to retrieve the results.

    Args:
        request: Chat request with message and optional conversation_id
        db: Database session
        background_tasks: Background tasks queue

    Returns:
        JobSubmissionResponse with job_id
    """
    job_service = get_job_service(db)

    # Create the job
    job = await job_service.create_job(
        job_type="chat",
        input_data={
            "message": request.message,
            "conversation_id": request.conversation_id,
        },
    )

    # Queue background processing
    if background_tasks:
        from app.config import get_settings
        settings = get_settings()
        background_tasks.add_task(
            process_chat_job,
            job.id,
            request.message,
            request.conversation_id,
            settings.async_database_url,
        )

    return JobSubmissionResponse(job_id=job.id)


@router.get("/{job_id}", response_model=JobResponse)
async def get_chat_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """Get the status and result of a chat job.

    Args:
        job_id: The ID of the job to retrieve
        db: Database session

    Returns:
        JobResponse with current status and results if available
    """
    job_service = get_job_service(db)
    job = await job_service.get_job(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return JobResponse.model_validate(job)


@router.post("/plan")
async def generate_plan(
    goal: str,
    context: dict | None = None,
    constraints: list[str] | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Generate a research plan directly without conversation.

    This endpoint bypasses the conversational interface and directly
    generates a plan based on the provided goal and context.

    Args:
        goal: Research goal description
        context: Optional context (organism, plant system, etc.)
        constraints: Optional list of constraints
        db: Database session

    Returns:
        Generated OPAL plan
    """
    try:
        from app.services.planner import get_planner_service

        planner_service = get_planner_service(db)
        plan = await planner_service.generate_plan(
            goal=goal,
            context=context,
            constraints=constraints,
        )
        return plan
    except LLMRefusalError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
