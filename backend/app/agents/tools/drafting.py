from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from app.services.retrieval.retriever import RAGRetriever
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DraftingInput(BaseModel):
    document_type: str = Field(
        description="Type of document to draft (e.g., 'field report', 'grant proposal', 'situation report')"
    )
    key_points: str = Field(description="Key points or raw notes to include in the draft")
    template_name: str = Field(
        default="", description="Optional: Name of template to use (if available in knowledge base)"
    )


class ReportDraftingTool(BaseTool):
    name: str = "draft_report"
    description: str = """Use this tool to draft humanitarian reports or grant proposals.
    Provide the document type, key points/raw notes, and optionally a template name.
    The tool will generate a structured draft based on available templates and best practices."""
    args_schema: type[BaseModel] = DraftingInput
    retriever: RAGRetriever

    def __init__(self, retriever: RAGRetriever) -> None:
        super().__init__(retriever=retriever)

    def _run(self, document_type: str, key_points: str, template_name: str = "") -> str:
        raise NotImplementedError("Use async version")

    async def _arun(self, document_type: str, key_points: str, template_name: str = "") -> str:
        try:
            logger.info("drafting_started", document_type=document_type)

            if template_name:
                query = f"Show me the template or guidelines for {template_name} {document_type}"
            else:
                query = f"What are the standard sections and requirements for a {document_type}?"

            chunks, citations = await self.retriever.retrieve(query)

            template_guidance = ""
            if chunks:
                template_guidance = "\n".join([chunk.content for chunk in chunks[:2]])

            draft = f"""DRAFT {document_type.upper()}

[This is a structured draft based on available templates and the provided information]

Key Information Provided:
{key_points}

Template Guidance:
{template_guidance if template_guidance else 'No specific template found. Using standard humanitarian reporting structure.'}

---

DRAFT STRUCTURE:

1. EXECUTIVE SUMMARY
   [Summarize the key points provided above in 2-3 paragraphs]

2. BACKGROUND/CONTEXT
   [Provide context based on the key points]

3. MAIN CONTENT
   [Organize the key points into logical sections]

4. RECOMMENDATIONS/NEXT STEPS
   [Based on the information provided, suggest next steps]

5. APPENDICES
   [List any supporting documents or data]

---

Note: This is a preliminary draft. Please review and customize based on specific donor/organizational requirements.

{f'Template sources: {", ".join([c.source_file for c in citations[:2]])}' if citations else ''}
"""

            logger.info("drafting_completed", document_type=document_type)
            return draft

        except Exception as e:
            logger.error("drafting_failed", error=str(e))
            return f"Drafting failed: {str(e)}"
