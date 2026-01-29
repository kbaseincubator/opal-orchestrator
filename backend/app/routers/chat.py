"""Chat API router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat import get_chat_service
from app.services.llm import LLMRefusalError
import logging

router = APIRouter(prefix="/chat", tags=["chat"])

logger = logging.getLogger(__name__)



@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """Process a chat message and return a response.

    The chat endpoint handles the conversational interface with the OPAL
    assistant. It maintains conversation state and can generate research
    plans based on user input.

    Args:
        request: Chat request with message and optional conversation_id
        db: Database session

    Returns:
        ChatResponse with assistant message, optional plan, and sources
    """

    try:
        logger.info(f"chat: {request}")
        print(request)
        chat_service = get_chat_service(db)
        logger.info("got chat service")
        print("got chat service")
        response = await chat_service.chat(
            message=request.message,
            conversation_id=request.conversation_id,
        )
        logger.info(f"got response: {response}")
        print("got response")
        return response
    except LLMRefusalError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


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
