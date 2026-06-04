from typing import Any

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.services.retrieval.retriever import RAGRetriever
from app.utils.logging import get_logger

logger = get_logger(__name__)


class ComplianceCheckInput(BaseModel):
    operational_data: str = Field(description="The operational data to check for compliance")
    standard_name: str = Field(
        description="The name of the global standard to check against (e.g., 'UN SDG', 'Sphere Standards')"
    )


class ComplianceCrossReferenceTool(BaseTool):
    name: str = "compliance_cross_reference"
    description: str = """Use this tool to cross-reference local operational data against global humanitarian standards.
    Provide the operational data and the name of the standard (e.g., UN SDG targets, Sphere Standards).
    The tool will identify gaps and compliance issues."""
    args_schema: type[BaseModel] = ComplianceCheckInput
    retriever: RAGRetriever

    def __init__(self, retriever: RAGRetriever) -> None:
        super().__init__(retriever=retriever)

    def _run(self, operational_data: str, standard_name: str) -> str:
        raise NotImplementedError("Use async version")

    async def _arun(self, operational_data: str, standard_name: str) -> str:
        try:
            logger.info("compliance_check_started", standard=standard_name)

            query = f"What are the requirements and standards for {standard_name}?"
            chunks, citations = await self.retriever.retrieve(query)

            if not chunks:
                return f"No information found about {standard_name} in the knowledge base. Please ensure relevant standards documents have been ingested."

            standard_requirements = "\n".join([chunk.content for chunk in chunks[:3]])

            analysis = f"""COMPLIANCE ANALYSIS

Standard: {standard_name}

Operational Data Provided:
{operational_data[:500]}...

Relevant Standard Requirements:
{standard_requirements[:1000]}...

Gap Analysis:
[Note: This is a simplified analysis. In production, this would use advanced LLM reasoning to identify specific gaps]

Based on the available standards documentation, please review your operational data against the requirements outlined above.
Key areas to verify:
1. Documentation completeness
2. Process adherence
3. Reporting requirements
4. Quality standards

Sources: {', '.join([c.source_file for c in citations[:3]])}
"""

            logger.info("compliance_check_completed", standard=standard_name)
            return analysis

        except Exception as e:
            logger.error("compliance_check_failed", error=str(e))
            return f"Compliance check failed: {str(e)}"
