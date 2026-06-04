from typing import Any

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from app.config import settings
from app.utils.logging import get_logger

logger = get_logger(__name__)


class BaseAgent:
    def __init__(self, llm: BaseChatModel, tools: list[BaseTool]) -> None:
        self.llm = llm
        self.tools = tools
        self.agent_executor = self._create_agent()

    def _create_agent(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are an AI assistant for humanitarian operations. You have access to tools that help you:
- Cross-reference compliance data against global standards
- Draft reports and grant proposals
- Match grant opportunities
- Monitor crisis alerts

Use these tools to provide accurate, helpful assistance. Always cite your sources and be transparent about limitations.""",
                ),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_openai_functions_agent(self.llm, self.tools, prompt)

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            max_iterations=settings.agent_max_iterations,
            handle_parsing_errors=True,
        )

    async def run(self, input_text: str) -> dict[str, Any]:
        try:
            logger.info("agent_execution_started", input=input_text[:100])
            result = await self.agent_executor.ainvoke({"input": input_text})
            logger.info("agent_execution_completed", output=str(result)[:100])
            return result
        except Exception as e:
            logger.error("agent_execution_failed", error=str(e))
            return {"output": f"Agent execution failed: {str(e)}", "error": str(e)}
