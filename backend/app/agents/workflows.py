from langchain_community.chat_models import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from app.agents.base import BaseAgent
from app.agents.tools.compliance import ComplianceCrossReferenceTool
from app.agents.tools.crisis_monitor import CrisisMonitorTool
from app.agents.tools.drafting import ReportDraftingTool
from app.agents.tools.grant_matching import GrantMatchingTool
from app.config import settings
from app.core.exceptions import LLMProviderError
from app.core.models import WorkflowRequest, WorkflowResponse, WorkflowType
from app.core.providers.external_feeds import ExternalFeed
from app.services.retrieval.retriever import RAGRetriever
from app.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowOrchestrator:
    def __init__(
        self,
        retriever: RAGRetriever,
        news_feed: ExternalFeed,
        weather_feed: ExternalFeed,
    ) -> None:
        self.retriever = retriever
        self.news_feed = news_feed
        self.weather_feed = weather_feed
        self.llm = self._create_llm()

    def _create_llm(self) -> BaseChatModel:
        if settings.llm_provider == "openai" and settings.openai_api_key:
            return ChatOpenAI(
                api_key=settings.openai_api_key,
                model=settings.llm_model,
                temperature=settings.llm_temperature,
            )
        elif settings.llm_provider == "anthropic" and settings.anthropic_api_key:
            from langchain_anthropic import ChatAnthropic

            return ChatAnthropic(
                api_key=settings.anthropic_api_key,
                model=settings.llm_model,
                temperature=settings.llm_temperature,
            )
        else:
            raise LLMProviderError(
                "LangChain agents require a real LLM provider. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY."
            )

    async def execute_workflow(self, request: WorkflowRequest) -> WorkflowResponse:
        try:
            logger.info("workflow_started", workflow_type=request.workflow_type.value)

            if request.workflow_type == WorkflowType.COMPLIANCE:
                result = await self._execute_compliance_workflow(request)
            elif request.workflow_type == WorkflowType.DRAFTING:
                result = await self._execute_drafting_workflow(request)
            elif request.workflow_type == WorkflowType.GRANT_MATCHING:
                result = await self._execute_grant_matching_workflow(request)
            elif request.workflow_type == WorkflowType.CRISIS_MONITOR:
                result = await self._execute_crisis_monitor_workflow(request)
            else:
                raise ValueError(f"Unknown workflow type: {request.workflow_type}")

            response = WorkflowResponse(
                workflow_type=request.workflow_type, status="completed", result=result
            )

            logger.info("workflow_completed", workflow_type=request.workflow_type.value)
            return response

        except Exception as e:
            logger.error("workflow_failed", workflow_type=request.workflow_type.value, error=str(e))
            return WorkflowResponse(
                workflow_type=request.workflow_type,
                status="failed",
                result={"error": str(e)},
            )

    async def _execute_compliance_workflow(self, request: WorkflowRequest) -> dict:
        tool = ComplianceCrossReferenceTool(retriever=self.retriever)
        agent = BaseAgent(llm=self.llm, tools=[tool])

        operational_data = request.parameters.get("operational_data", "")
        standard_name = request.parameters.get("standard_name", "UN SDG")

        input_text = f"Check compliance of the following operational data against {standard_name}: {operational_data}"
        result = await agent.run(input_text)

        return {"output": result.get("output", ""), "standard": standard_name}

    async def _execute_drafting_workflow(self, request: WorkflowRequest) -> dict:
        tool = ReportDraftingTool(retriever=self.retriever)
        agent = BaseAgent(llm=self.llm, tools=[tool])

        document_type = request.parameters.get("document_type", "field report")
        key_points = request.parameters.get("key_points", "")
        template_name = request.parameters.get("template_name", "")

        input_text = f"Draft a {document_type} with these key points: {key_points}"
        if template_name:
            input_text += f" using the {template_name} template"

        result = await agent.run(input_text)

        return {"output": result.get("output", ""), "document_type": document_type}

    async def _execute_grant_matching_workflow(self, request: WorkflowRequest) -> dict:
        tool = GrantMatchingTool(retriever=self.retriever)
        agent = BaseAgent(llm=self.llm, tools=[tool])

        project_description = request.parameters.get("project_description", "")
        focus_area = request.parameters.get("focus_area", "general humanitarian")
        budget_range = request.parameters.get("budget_range", "")

        input_text = f"Find grant opportunities for this project in {focus_area}: {project_description}"
        if budget_range:
            input_text += f" with budget range {budget_range}"

        result = await agent.run(input_text)

        return {"output": result.get("output", ""), "focus_area": focus_area}

    async def _execute_crisis_monitor_workflow(self, request: WorkflowRequest) -> dict:
        tool = CrisisMonitorTool(news_feed=self.news_feed, weather_feed=self.weather_feed)
        agent = BaseAgent(llm=self.llm, tools=[tool])

        region = request.parameters.get("region", "global")
        alert_types = request.parameters.get("alert_types", "all")

        input_text = f"Monitor crisis alerts for {region} region, alert types: {alert_types}"
        result = await agent.run(input_text)

        return {"output": result.get("output", ""), "region": region}
