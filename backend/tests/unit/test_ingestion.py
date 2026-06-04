import pytest

from app.core.models import DocumentChunk
from app.services.ingestion.chunker import DocumentChunker


class TestDocumentChunker:
    @pytest.mark.asyncio
    async def test_chunk_documents_basic(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)

        pages = [
            {
                "page": 1,
                "content": "This is a test document. " * 20,
            }
        ]

        chunks = await chunker.chunk_documents(pages, "test.pdf")

        assert len(chunks) > 0
        assert all(isinstance(chunk, DocumentChunk) for chunk in chunks)
        assert all(chunk.source_file == "test.pdf" for chunk in chunks)
        assert all(chunk.page == 1 for chunk in chunks)

    @pytest.mark.asyncio
    async def test_chunk_documents_multiple_pages(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)

        pages = [
            {"page": 1, "content": "Page one content. " * 10},
            {"page": 2, "content": "Page two content. " * 10},
        ]

        chunks = await chunker.chunk_documents(pages, "test.pdf")

        assert len(chunks) > 0
        page_numbers = {chunk.page for chunk in chunks}
        assert 1 in page_numbers
        assert 2 in page_numbers

    @pytest.mark.asyncio
    async def test_chunk_documents_with_section(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)

        pages = [
            {
                "page": None,
                "section": "Introduction",
                "content": "Introduction section content. " * 10,
            }
        ]

        chunks = await chunker.chunk_documents(pages, "test.xlsx")

        assert len(chunks) > 0
        assert all(chunk.section == "Introduction" for chunk in chunks)
        assert all(chunk.page is None for chunk in chunks)
