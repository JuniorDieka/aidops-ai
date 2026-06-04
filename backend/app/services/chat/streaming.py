from typing import AsyncIterator

from app.core.models import ChatMessage, Citation, MessageRole, StreamChunk
from app.core.providers.llm import LLMProvider
from app.services.retrieval.retriever import RAGRetriever
from app.utils.logging import get_logger

logger = get_logger(__name__)


class StreamingChatService:
    def __init__(self, llm_provider: LLMProvider, retriever: RAGRetriever) -> None:
        self.llm_provider = llm_provider
        self.retriever = retriever

    async def stream_response(
        self, query: str, chat_history: list[ChatMessage]
    ) -> AsyncIterator[StreamChunk]:
        try:
            context, citations = await self.retriever.retrieve_with_context(query)

            yield StreamChunk(type="context_retrieved", metadata={"citation_count": len(citations)})

            for citation in citations:
                yield StreamChunk(type="citation", citation=citation)

            system_prompt = self._build_system_prompt(context)
            messages = [ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)]
            messages.extend(chat_history[-5:])
            messages.append(ChatMessage(role=MessageRole.USER, content=query))

            yield StreamChunk(type="stream_start")

            async for token in self.llm_provider.stream(messages):
                yield StreamChunk(type="token", content=token)

            yield StreamChunk(type="stream_end")

        except Exception as e:
            logger.error("streaming_failed", error=str(e))
            yield StreamChunk(
                type="error",
                content=f"I encountered an error while processing your request: {str(e)}",
            )

    def _build_system_prompt(self, context: str) -> str:
        return f"""You are an AI assistant for humanitarian operations. Your role is to provide accurate, helpful information based on the provided context.

CRITICAL INSTRUCTIONS:
1. Base your answers ONLY on the provided context below
2. If the context doesn't contain enough information to answer the question, explicitly say so
3. Never fabricate or hallucinate information, especially regarding compliance, legal matters, or operational procedures
4. When citing information, reference the source document and page number
5. If you're uncertain about any aspect of your answer, clearly state your uncertainty
6. For humanitarian data, be especially careful about accuracy - lives may depend on correct information

CONTEXT:
{context}

Remember: It's better to say "I don't have enough information" than to provide potentially incorrect information in a humanitarian context."""
