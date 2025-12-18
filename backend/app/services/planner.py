"""Planning service for generating OPAL resource deployment plans."""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import (
    Citation,
    OPALPlan,
    PlanStep,
    RiskItem,
)
from app.services.llm import get_llm_service
from app.services.retrieval import RetrievalService, get_retrieval_service


PLANNER_SYSTEM_PROMPT = """You are an expert research planner for the OPAL (Organized Production of Agile Livelihoods) network. Your task is to create detailed, actionable research plans that leverage capabilities across multiple OPAL member labs.

When creating a plan:

1. STRUCTURE: Organize the plan into clear phases:
   - Discovery/Characterization phase (strain selection, initial testing)
   - Design/Build phase (genetic engineering, strain construction)
   - Test phase (phenotyping, validation)
   - Scale-up/Application phase (if applicable)

2. SEQUENCING: Optimize for "fastest learning":
   - Front-load experiments that reduce uncertainty
   - Identify what can run in parallel
   - Mark critical decision points where results gate next steps

3. DEPENDENCIES: Clearly specify:
   - What inputs each step requires
   - What outputs it produces
   - Which steps depend on which other steps

4. CONSTRAINTS: For each step, note:
   - Biosafety requirements
   - Sample format requirements
   - Throughput/capacity limitations
   - Shipping/transfer logistics between labs

5. CITATIONS: Every capability recommendation MUST cite the source document.
   - If no source exists, mark the step as "is_hypothesis: true"
   - Be honest about uncertainty

6. RISKS: Identify potential issues and provide alternatives:
   - What if a capability is at capacity?
   - What if initial results are negative?
   - What are backup approaches?

Return a complete, well-structured plan that a scientist can immediately begin executing."""


class PlannerService:
    """Service for generating detailed research plans."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.llm_service = get_llm_service()
        self.retrieval_service = get_retrieval_service(db)

    async def generate_plan(
        self,
        goal: str,
        context: Optional[dict] = None,
        constraints: Optional[list[str]] = None,
    ) -> OPALPlan:
        """Generate a research plan for a given goal.

        Args:
            goal: Research goal description
            context: Optional context (organism, plant system, etc.)
            constraints: Optional list of constraints

        Returns:
            Complete OPALPlan
        """
        # Search for relevant capabilities
        capabilities = await self.retrieval_service.search_capabilities(
            query=goal,
            top_k=20,
        )

        # Build context for the LLM
        capability_context = []
        for cap in capabilities:
            cap_info = {
                "name": cap.capability.name,
                "facility": cap.capability.facility_name,
                "lab": f"{cap.capability.lab_name} ({cap.capability.lab_institution})",
                "description": cap.capability.description,
                "modalities": cap.capability.modalities,
                "throughput": cap.capability.throughput,
                "constraints": cap.capability.constraints,
                "source_citations": [
                    {"source_id": c.source_document_id, "quote": c.text}
                    for c in cap.source_chunks[:2]
                ],
            }
            capability_context.append(cap_info)

        # Build the prompt
        context_str = ""
        if context:
            context_str = f"\n\nProject Context:\n{self._format_context(context)}"

        constraints_str = ""
        if constraints:
            constraints_str = f"\n\nConstraints:\n" + "\n".join(f"- {c}" for c in constraints)

        user_message = f"""Research Goal: {goal}
{context_str}
{constraints_str}

Available OPAL Capabilities (from capability registry):
{self._format_capabilities(capability_context)}

Please create a detailed OPAL Resource Deployment Plan. Return it as a JSON object with this structure:
{{
    "goal_summary": "...",
    "assumptions": ["..."],
    "steps": [
        {{
            "step_id": "S1",
            "objective": "...",
            "recommended_facility": "Lab Name - Facility Name",
            "capability_ids": ["..."],
            "inputs": ["..."],
            "outputs": ["..."],
            "constraints": ["..."],
            "dependencies": [],
            "decision_points": ["..."],
            "citations": [{{"source_document_id": "...", "quote": "..."}}],
            "is_hypothesis": false
        }}
    ],
    "open_questions": ["..."],
    "risks_and_alternatives": [
        {{"risk": "...", "impact": "...", "alternative": "..."}}
    ]
}}"""

        response = self.llm_service.generate(
            messages=[{"role": "user", "content": user_message}],
            system=PLANNER_SYSTEM_PROMPT,
            max_tokens=4096,
        )

        # Parse the response
        plan = self._parse_plan_from_response(response["content"])
        return plan

    def _format_context(self, context: dict) -> str:
        """Format context dict into readable string."""
        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)

    def _format_capabilities(self, capabilities: list[dict]) -> str:
        """Format capabilities list for the prompt."""
        lines = []
        for i, cap in enumerate(capabilities, 1):
            lines.append(f"\n{i}. {cap['name']} ({cap['lab']} - {cap['facility']})")
            if cap.get("description"):
                lines.append(f"   Description: {cap['description']}")
            if cap.get("modalities"):
                lines.append(f"   Modalities: {', '.join(cap['modalities'])}")
            if cap.get("throughput"):
                lines.append(f"   Throughput: {cap['throughput']}")
            if cap.get("constraints"):
                lines.append(f"   Constraints: {cap['constraints']}")
            if cap.get("source_citations"):
                for cit in cap["source_citations"]:
                    lines.append(f"   Source: {cit['source_id']}")
        return "\n".join(lines)

    def _parse_plan_from_response(self, response: str) -> OPALPlan:
        """Parse plan JSON from LLM response."""
        import json
        import re

        # Try to extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if not json_match:
            # Return empty plan if no JSON found
            return OPALPlan(
                goal_summary="Failed to parse plan",
                assumptions=["LLM response did not contain valid JSON"],
                steps=[],
                open_questions=["Please try again with a clearer goal description"],
                risks_and_alternatives=[],
            )

        try:
            plan_data = json.loads(json_match.group())
        except json.JSONDecodeError:
            return OPALPlan(
                goal_summary="Failed to parse plan",
                assumptions=["JSON parsing error"],
                steps=[],
                open_questions=["Please try again"],
                risks_and_alternatives=[],
            )

        # Build plan object
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


def get_planner_service(db: AsyncSession) -> PlannerService:
    """Get a planner service instance."""
    return PlannerService(db)
