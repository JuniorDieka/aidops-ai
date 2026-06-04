import pytest

from app.core.exceptions import InsufficientContextError
from app.core.models import DocumentChunk
from app.core.providers.embeddings import LocalEmbeddingProvider
from app.core.providers.vectorstore import FAISSVectorStore
from app.services.retrieval.retriever import RAGRetriever


class TestRAGRetriever:
    @pytest.mark.asyncio
    async def test_retrieve_with_results(self):
        embedding_provider = LocalEmbeddingProvider()
        vector_store = FAISSVectorStore(dimension=384, index_path="./test_index_retrieve")

        chunk = DocumentChunk(
            content="Humanitarian operations require clean water access.",
            source_file="test.pdf",
            page=1,
            embedding=await embedding_provider.embed_text(
                "Humanitarian operations require clean water access."
            ),
        )

        await vector_store.add_chunks([chunk])

        retriever = RAGRetriever(
            embedding_provider=embedding_provider,
            vector_store=vector_store,
            score_threshold=0.0,
        )

        chunks, citations = await retriever.retrieve("water access humanitarian")

        assert len(chunks) > 0
        assert len(citations) > 0
        assert citations[0].source_file == "test.pdf"

    @pytest.mark.asyncio
    async def test_retrieve_insufficient_context(self):
        embedding_provider = LocalEmbeddingProvider()
        vector_store = FAISSVectorStore(dimension=384, index_path="./test_index_empty")

        retriever = RAGRetriever(
            embedding_provider=embedding_provider,
            vector_store=vector_store,
            score_threshold=0.9,
        )

        with pytest.raises(InsufficientContextError):
            await retriever.retrieve("completely unrelated query about space travel")
