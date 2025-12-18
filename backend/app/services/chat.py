"""Chat orchestration service for the OPAL assistant."""

import json
import logging
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from sqlalchemy import select

from app.models import Conversation
from app.models.schemas import (
    ChatMessage,
    ChatResponse,
    Citation,
    OPALPlan,
    PlanStep,
    RiskItem,
    SearchResult,
)
from app.services.llm import get_llm_service
from app.services.retrieval import RetrievalService, get_retrieval_service


SYSTEM_PROMPT = """You are the OPAL Orchestration Assistant, an expert AI that helps scientists plan cross-lab biological research projects across the OPAL (Orchestrated Platform for Autonomous Laboratories) network.

Your role is to:
1. Understand the scientist's research goal and constraints
2. Search the OPAL capability registry to find relevant labs, facilities, and capabilities
3. Create a structured, sequenced research plan that leverages multiple OPAL labs
4. Provide citations for every recommendation from source documents

IMPORTANT RULES:
- NEVER fabricate capabilities. Only recommend what exists in the capability registry.
- Every recommendation MUST have a citation from source documents.
- If you cannot find a capability in the sources, clearly label it as a "hypothesis" or "assumption"
- Ask clarifying questions to understand: organism type, plant system, environmental constraints, biosafety level, timeline, and existing resources
- Stop asking questions if the user says "assume reasonable defaults" or similar

When creating a plan, consider:
- Which experiments provide the most information earliest ("fastest learning path")
- What can run in parallel vs. what requires sequential dependencies
- Rate-limiting steps that may require special attention (e.g., protein engineering)
- Sample formats, biosafety requirements, and logistics between labs
- Fallback options if a primary capability is unavailable

You have access to these tools:
- search_capabilities: Search the OPAL capability registry
- get_lab_info: Get details about a specific lab
- get_capability_details: Get full details about a capability
- create_plan: Finalize and structure a research plan

Always be helpful, scientifically rigorous, and honest about limitations."""


CLARIFYING_QUESTIONS = [
    "What is your target organism or chassis strain (e.g., E. coli, Pseudomonas, yeast)?",
    "What plant system will you be testing with (e.g., Arabidopsis, poplar, switchgrass)?",
    "Are there specific environmental conditions of interest (drought, salinity, temperature)?",
    "What biosafety level is required for your work?",
    "Do you have any existing strains, libraries, or preliminary data to build upon?",
    "What is your approximate timeline or deadline for this project?",
]


class ChatService:
    """Service for managing chat conversations with the OPAL assistant."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm_service = get_llm_service()
        self.retrieval_service = get_retrieval_service(db)

    def _get_tools(self) -> list[dict]:
        """Get tool definitions for the LLM."""
        return [
            {
                "name": "search_capabilities",
                "description": "Search the OPAL capability registry for relevant capabilities, facilities, and labs. Use this to find what resources are available across the OPAL network.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query describing the capability needed",
                        },
                        "modality": {
                            "type": "string",
                            "description": "Optional filter by modality (e.g., 'phenotyping', 'sequencing', 'proteomics')",
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional filter by tags",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "get_lab_info",
                "description": "Get detailed information about a specific OPAL member lab",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "lab_name": {
                            "type": "string",
                            "description": "Name of the lab to look up",
                        },
                    },
                    "required": ["lab_name"],
                },
            },
            {
                "name": "create_plan",
                "description": "Create a structured OPAL Resource Deployment Plan. Call this when you have gathered enough information and are ready to propose a plan.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "goal_summary": {
                            "type": "string",
                            "description": "Brief summary of the research goal",
                        },
                        "assumptions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key assumptions made in the plan",
                        },
                        "steps": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "step_id": {"type": "string"},
                                    "objective": {"type": "string"},
                                    "recommended_facility": {"type": "string"},
                                    "capability_ids": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "inputs": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "outputs": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "constraints": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "dependencies": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "decision_points": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                    "citations": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "source_document_id": {"type": "string"},
                                                "quote": {"type": "string"},
                                            },
                                        },
                                    },
                                    "is_hypothesis": {"type": "boolean"},
                                },
                                "required": ["step_id", "objective", "recommended_facility"],
                            },
                        },
                        "open_questions": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "risks_and_alternatives": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "risk": {"type": "string"},
                                    "impact": {"type": "string"},
                                    "alternative": {"type": "string"},
                                },
                            },
                        },
                    },
                    "required": ["goal_summary", "steps"],
                },
            },
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        """Execute a tool and return the result."""
        logger.info(f"Executing tool: {tool_name} with input: {tool_input}")
        try:
            result = await self._execute_tool_impl(tool_name, tool_input)
            logger.info(f"Tool {tool_name} returned: {str(result)[:200]}...")
            return result
        except Exception as e:
            logger.error(f"Tool {tool_name} failed: {e}", exc_info=True)
            return {"error": str(e)}

    async def _execute_tool_impl(self, tool_name: str, tool_input: dict) -> dict:
        """Internal tool execution implementation."""
        if tool_name == "search_capabilities":
            results = await self.retrieval_service.search_capabilities(
                query=tool_input["query"],
                modality=tool_input.get("modality"),
                tags=tool_input.get("tags"),
                top_k=10,
            )
            return {
                "capabilities": [
                    {
                        "name": r.capability.name,
                        "description": r.capability.description,
                        "facility": r.capability.facility_name,
                        "lab": r.capability.lab_name,
                        "institution": r.capability.lab_institution,
                        "modalities": r.capability.modalities,
                        "throughput": r.capability.throughput,
                        "constraints": r.capability.constraints,
                        "relevance_score": r.relevance_score,
                        "citations": [
                            {
                                "source_document_id": c.source_document_id,
                                "source_title": c.source_title,
                                "quote": c.text[:200] + "..." if len(c.text) > 200 else c.text,
                            }
                            for c in r.source_chunks[:2]
                        ],
                    }
                    for r in results
                ]
            }

        elif tool_name == "get_lab_info":
            labs = await self.retrieval_service.get_all_labs()
            lab_name = tool_input["lab_name"].lower()
            for lab in labs:
                if lab_name in lab.name.lower():
                    capabilities = await self.retrieval_service.get_lab_capabilities(lab.id)
                    return {
                        "name": lab.name,
                        "institution": lab.institution,
                        "location": lab.location,
                        "description": lab.description,
                        "capabilities": [
                            {
                                "name": c.name,
                                "description": c.description,
                                "modalities": c.modalities,
                            }
                            for c in capabilities
                        ],
                    }
            return {"error": f"Lab '{tool_input['lab_name']}' not found"}

        elif tool_name == "create_plan":
            # The LLM provides the plan structure, we just validate and return it
            return {"status": "plan_created", "plan": tool_input}

        return {"error": f"Unknown tool: {tool_name}"}

    async def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
    ) -> ChatResponse:
        """Process a chat message and return a response.

        Args:
            message: User's message
            conversation_id: Optional conversation ID for continuity

        Returns:
            ChatResponse with message, plan (if created), and sources
        """
        # Get or create conversation from database
        conversation_record = None
        if conversation_id:
            result = await self.db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation_record = result.scalar_one_or_none()

        if not conversation_record:
            # Create new conversation
            conversation_id = str(uuid.uuid4())
            conversation_record = Conversation(
                id=conversation_id,
                messages=[],
            )
            self.db.add(conversation_record)
            await self.db.flush()
            logger.info(f"Created new conversation: {conversation_id}")
        else:
            logger.info(f"Found existing conversation: {conversation_id} with {len(conversation_record.messages)} messages")

        # Get messages list from record
        conversation = list(conversation_record.messages)

        # Add user message
        conversation.append({"role": "user", "content": message})

        # Generate response with tools using async tool executor
        response = await self.llm_service.generate_with_tools(
            messages=conversation,
            tools=self._get_tools(),
            system=SYSTEM_PROMPT,
            tool_executor=self._execute_tool,
        )

        # Extract plan if created
        plan = None
        sources = []
        for tool_result in response.get("all_tool_results", []):
            if tool_result["tool_name"] == "create_plan":
                plan_data = tool_result["tool_result"].get("plan", {})
                plan = self._parse_plan(plan_data)
            elif tool_result["tool_name"] == "search_capabilities":
                # Extract sources from search results
                for cap in tool_result["tool_result"].get("capabilities", []):
                    for citation in cap.get("citations", []):
                        sources.append(SearchResult(
                            chunk_id="",
                            source_document_id=citation.get("source_document_id", ""),
                            source_title=citation.get("source_title", ""),
                            text=citation.get("quote", ""),
                            score=cap.get("relevance_score", 0),
                            metadata={},
                        ))

        # Add assistant message to conversation
        conversation.append({"role": "assistant", "content": response["content"]})

        # Persist conversation to database
        conversation_record.messages = conversation
        if plan:
            # Use mode='json' to ensure datetime objects are serialized as strings
            conversation_record.plan = plan.model_dump(mode='json') if hasattr(plan, 'model_dump') else None

        # Persist sources (append new sources to existing)
        if sources:
            existing_sources = conversation_record.sources or []
            existing_ids = {s.get("chunk_id") for s in existing_sources}
            new_sources = [
                s.model_dump(mode='json') if hasattr(s, 'model_dump') else s
                for s in sources
                if (s.chunk_id if hasattr(s, 'chunk_id') else s.get("chunk_id")) not in existing_ids
            ]
            conversation_record.sources = existing_sources + new_sources

        # Auto-generate title from first user message if not set
        if not conversation_record.title and len(conversation) >= 1:
            first_user_msg = next((m["content"] for m in conversation if m["role"] == "user"), None)
            if first_user_msg:
                conversation_record.title = first_user_msg[:100] + ("..." if len(first_user_msg) > 100 else "")

        await self.db.commit()

        return ChatResponse(
            message=response["content"],
            conversation_id=conversation_id,
            plan=plan,
            sources=sources,
        )

    def _parse_plan(self, plan_data: dict) -> OPALPlan:
        """Parse plan data from tool call into OPALPlan object."""
        steps = []
        for step_data in plan_data.get("steps", []):
            citations = []
            for cit in step_data.get("citations", []):
                citations.append(Citation(
                    source_document_id=cit.get("source_document_id", ""),
                    quote=cit.get("quote", ""),
                ))
            steps.append(PlanStep(
                step_id=step_data.get("step_id", ""),
                objective=step_data.get("objective", ""),
                recommended_facility=step_data.get("recommended_facility", ""),
                capability_ids=step_data.get("capability_ids", []),
                inputs=step_data.get("inputs", []),
                outputs=step_data.get("outputs", []),
                constraints=step_data.get("constraints", []),
                dependencies=step_data.get("dependencies", []),
                decision_points=step_data.get("decision_points", []),
                citations=citations,
                is_hypothesis=step_data.get("is_hypothesis", False),
            ))

        risks = []
        for risk_data in plan_data.get("risks_and_alternatives", []):
            risks.append(RiskItem(
                risk=risk_data.get("risk", ""),
                impact=risk_data.get("impact", ""),
                alternative=risk_data.get("alternative"),
            ))

        return OPALPlan(
            goal_summary=plan_data.get("goal_summary", ""),
            assumptions=plan_data.get("assumptions", []),
            steps=steps,
            open_questions=plan_data.get("open_questions", []),
            risks_and_alternatives=risks,
        )


def get_chat_service(db: AsyncSession) -> ChatService:
    """Get a chat service instance."""
    return ChatService(db)
