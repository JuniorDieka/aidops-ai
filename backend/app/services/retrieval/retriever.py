from typing import Any

from app.config import settings
from app.core.exceptions import InsufficientContextError, RetrievalError
from app.core.models import Citation, DocumentChunk
from app.core.providers.embeddings import EmbeddingProvider
from app.core.providers.vectorstore import VectorStoreProvider
from app.utils.logging import get_logger

logger = get_logger(__name__)


class RAGRetriever:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStoreProvider,
        top_k: int = settings.retrieval_top_k,
        score_threshold: float = settings.retrieval_score_threshold,
    ) -> None:
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.top_k = top_k
        self.score_threshold = score_threshold

    async def retrieve(
        self, query: str, filter_metadata: dict[str, Any] | None = None
    ) -> tuple[list[DocumentChunk], list[Citation]]:
        try:
            logger.info("retrieval_started", query=query[:100])

            query_embedding = await self.embedding_provider.embed_text(query)

            results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=self.top_k,
                filter_metadata=filter_metadata,
            )

            filtered_results = [
                (chunk, score) for chunk, score in results if score >= self.score_threshold
            ]

            if not filtered_results:
                logger.warning("no_relevant_context", query=query[:100])
                raise InsufficientContextError(
                    "No relevant context found for the query. "
                    "Please ensure documents have been ingested or try rephrasing your question."
                )

            chunks = [chunk for chunk, _ in filtered_results]
            citations = [
                Citation(
                    source_file=chunk.source_file,
                    page=chunk.page,
                    section=chunk.section,
                    chunk_id=chunk.id,
                    score=score,
                    text=chunk.content[:200],
                )
                for chunk, score in filtered_results
            ]

            logger.info(
                "retrieval_completed",
                query=query[:100],
                results=len(chunks),
                avg_score=sum(c.score for c in citations) / len(citations) if citations else 0,
            )

            return chunks, citations

        except InsufficientContextError:
            raise
        except Exception as e:
            logger.error("retrieval_failed", query=query[:100], error=str(e))
            raise RetrievalError(f"Retrieval failed: {str(e)}")

    async def retrieve_with_context(
        self, query: str, filter_metadata: dict[str, Any] | None = None
    ) -> tuple[str, list[Citation]]:
        chunks, citations = await self.retrieve(query, filter_metadata)

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source_info = f"[Source {i}: {chunk.source_file}"
            if chunk.page:
                source_info += f", Page {chunk.page}"
            if chunk.section:
                source_info += f", Section: {chunk.section}"
            source_info += "]"

            context_parts.append(f"{source_info}\n{chunk.content}\n")

        context = "\n---\n".join(context_parts)

        return context, citations
