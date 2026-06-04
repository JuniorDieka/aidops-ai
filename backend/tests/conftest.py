import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def mock_llm_provider():
    from app.core.providers.llm import MockLLMProvider

    return MockLLMProvider()


@pytest.fixture
def mock_embedding_provider():
    from app.core.providers.embeddings import LocalEmbeddingProvider

    return LocalEmbeddingProvider()


@pytest.fixture
def mock_vector_store():
    from app.core.providers.vectorstore import FAISSVectorStore

    return FAISSVectorStore(dimension=384, index_path="./test_faiss_index")


@pytest.fixture
def sample_document_chunk():
    from app.core.models import DocumentChunk

    return DocumentChunk(
        content="This is a test document about humanitarian operations.",
        source_file="test.pdf",
        page=1,
        language="en",
        embedding=[0.1] * 384,
    )
