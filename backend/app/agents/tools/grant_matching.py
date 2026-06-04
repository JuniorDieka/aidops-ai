from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.services.retrieval.retriever import RAGRetriever
from app.utils.logging import get_logger

logger = get_logger(__name__)


class GrantMatchingInput(BaseModel):
    project_description: str = Field(
        description="Description of the project or program seeking funding"
    )
    focus_area: str = Field(
        description="Primary focus area (e.g., 'health', 'education', 'water/sanitation', 'emergency response')"
    )
    budget_range: str = Field(
        default="", description="Optional: Budget range needed (e.g., '$50k-$100k')"
    )


class GrantMatchingTool(BaseTool):
    name: str = "match_grants"
    description: str = """Use this tool to find matching grant opportunities for humanitarian projects.
    Provide a project description, focus area, and optionally a budget range.
    The tool will search for relevant funding opportunities and provide a proposal outline."""
    args_schema: type[BaseModel] = GrantMatchingInput
    retriever: RAGRetriever

    def __init__(self, retriever: RAGRetriever) -> None:
        super().__init__(retriever=retriever)

    def _run(self, project_description: str, focus_area: str, budget_range: str = "") -> str:
        raise NotImplementedError("Use async version")

    async def _arun(
        self, project_description: str, focus_area: str, budget_range: str = ""
    ) -> str:
        try:
            logger.info("grant_matching_started", focus_area=focus_area)

            query = f"Grant opportunities and funding sources for {focus_area} humanitarian projects"
            chunks, citations = await self.retriever.retrieve(query)

            grant_info = ""
            if chunks:
                grant_info = "\n\n".join([chunk.content for chunk in chunks[:3]])

            mock_opportunities = [
                {
                    "name": "[DEMO] Global Health Initiative Grant",
                    "funder": "Mock Foundation",
                    "amount": "$50,000 - $200,000",
                    "deadline": "Rolling",
                    "match_score": "85%",
                },
                {
                    "name": "[DEMO] Emergency Response Fund",
                    "funder": "Mock International Aid",
                    "amount": "$25,000 - $100,000",
                    "deadline": "Quarterly",
                    "match_score": "72%",
                },
            ]

            result = f"""GRANT MATCHING RESULTS

Project: {project_description[:200]}...
Focus Area: {focus_area}
{f'Budget Range: {budget_range}' if budget_range else ''}

---

MATCHING OPPORTUNITIES:

"""

            for i, opp in enumerate(mock_opportunities, 1):
                result += f"""{i}. {opp['name']}
   Funder: {opp['funder']}
   Amount: {opp['amount']}
   Deadline: {opp['deadline']}
   Match Score: {opp['match_score']}

"""

            result += f"""---

RELEVANT GRANT GUIDELINES FROM KNOWLEDGE BASE:
{grant_info if grant_info else 'No specific grant guidelines found in knowledge base. Consider ingesting relevant grant documentation.'}

---

PROPOSAL OUTLINE:

1. Project Summary
   - Align with funder priorities
   - Highlight {focus_area} impact

2. Needs Assessment
   - Demonstrate evidence-based need
   - Show community engagement

3. Project Design
   - Clear objectives and activities
   - Measurable outcomes

4. Budget & Sustainability
   - Detailed budget breakdown
   - Long-term sustainability plan

5. Organizational Capacity
   - Track record in {focus_area}
   - Team qualifications

{f'Sources: {", ".join([c.source_file for c in citations[:2]])}' if citations else ''}

Note: In production mode, this would query real grant databases and APIs.
"""

            logger.info("grant_matching_completed", opportunities=len(mock_opportunities))
            return result

        except Exception as e:
            logger.error("grant_matching_failed", error=str(e))
            return f"Grant matching failed: {str(e)}"
