from typing import AsyncIterator

from app.core.exceptions import InsufficientContextError
from app.core.models import ChatMessage, Citation, MessageRole, StreamChunk
from app.core.providers.llm import LLMProvider
from app.services.retrieval.retriever import RAGRetriever
from app.utils.logging import get_logger

logger = get_logger(__name__)


class StreamingChatService:
    def __init__(self, llm_provider: LLMProvider, retriever: RAGRetriever) -> None:
        self.llm_provider = llm_provider
        self.retriever = retriever

    def _is_greeting(self, query: str) -> bool:
        """Check if the query is a greeting."""
        greetings = ["hello", "hi", "hey", "greetings", "good morning", "good afternoon", "good evening"]
        query_lower = query.lower().strip()
        return any(greeting in query_lower for greeting in greetings) and len(query_lower.split()) <= 3

    async def _get_document_count(self) -> int:
        """Get the count of documents in the vector store."""
        try:
            return await self.retriever.vector_store.count()
        except Exception:
            return 0

    async def stream_response(
        self, query: str, chat_history: list[ChatMessage]
    ) -> AsyncIterator[StreamChunk]:
        try:
            # Check if it's a greeting
            if self._is_greeting(query):
                doc_count = await self._get_document_count()
                
                yield StreamChunk(type="stream_start")
                
                if doc_count == 0:
                    greeting_response = (
                        "Hello! 👋 Welcome to AidOps AI - your AI assistant for humanitarian operations.\n\n"
                        "I notice you haven't uploaded any documents yet. To get started:\n\n"
                        "1. Click the 📎 **paperclip icon** below to upload files (PDF, CSV, XLSX, MP3, WAV)\n"
                        "2. Or click **Upload Files** in the sidebar to add documents\n"
                        "3. Or try **Load Sample Data** to explore with demo humanitarian budget data\n\n"
                        "Once you've added documents, you can ask me questions like:\n"
                        "- 'Summarize the budget allocation'\n"
                        "- 'What are the main expense categories?'\n"
                        "- 'Show me compliance requirements'\n\n"
                        "How can I help you today?"
                    )
                else:
                    greeting_response = (
                        f"Hello! 👋 I'm your AI assistant for humanitarian operations.\n\n"
                        f"I currently have access to **{doc_count} document chunks** in my knowledge base. "
                        f"You can ask me questions about your data, request compliance checks, draft reports, or explore workflows.\n\n"
                        f"What would you like to know?"
                    )
                
                # Stream the greeting word by word
                words = greeting_response.split()
                for word in words:
                    yield StreamChunk(type="token", content=word + " ")
                
                yield StreamChunk(type="stream_end")
                return

            # Normal RAG flow for non-greeting queries
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

        except InsufficientContextError as e:
            logger.warning("no_context_found", query=query[:100])
            doc_count = await self._get_document_count()
            
            yield StreamChunk(type="stream_start")
            
            if doc_count == 0:
                error_message = (
                    "I couldn't find any documents to answer your question. 📚\n\n"
                    "To get started:\n"
                    "1. Click the 📎 **paperclip icon** below to upload files\n"
                    "2. Or click **Upload Files** in the sidebar\n"
                    "3. Or try **Load Sample Data** for a demo\n\n"
                    "Once you've uploaded documents, I'll be able to answer questions about them!"
                )
            else:
                error_message = (
                    f"I couldn't find relevant information in the {doc_count} document chunks I have access to. "
                    f"Try:\n"
                    f"- Rephrasing your question\n"
                    f"- Uploading more relevant documents\n"
                    f"- Asking about topics covered in your uploaded files"
                )
            
            words = error_message.split()
            for word in words:
                yield StreamChunk(type="token", content=word + " ")
            
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
