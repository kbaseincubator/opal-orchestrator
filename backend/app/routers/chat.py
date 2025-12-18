"""Chat API router."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat import get_chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


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
    chat_service = get_chat_service(db)
    response = await chat_service.chat(
        message=request.message,
        conversation_id=request.conversation_id,
    )
    return response


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
    from app.services.planner import get_planner_service

    planner_service = get_planner_service(db)
    plan = await planner_service.generate_plan(
        goal=goal,
        context=context,
        constraints=constraints,
    )
    return plan
