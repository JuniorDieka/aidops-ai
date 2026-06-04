from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings
from app.core.models import DocumentChunk
from app.utils.logging import get_logger

logger = get_logger(__name__)


class DocumentChunker:
    def __init__(
        self, chunk_size: int = settings.chunk_size, chunk_overlap: int = settings.chunk_overlap
    ) -> None:
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    async def chunk_documents(
        self, pages: list[dict[str, str | int]], source_file: str, language: str = "en"
    ) -> list[DocumentChunk]:
        chunks = []

        for page_data in pages:
            content = page_data["content"]
            page = page_data.get("page")
            section = page_data.get("section")

            text_chunks = self.text_splitter.split_text(content)

            for chunk_text in text_chunks:
                chunk = DocumentChunk(
                    content=chunk_text,
                    source_file=source_file,
                    page=page,
                    section=section,
                    language=language,
                    metadata={
                        "chunk_length": len(chunk_text),
                        "source_type": self._infer_source_type(source_file),
                    },
                )
                chunks.append(chunk)

        logger.info(
            "documents_chunked",
            source_file=source_file,
            pages=len(pages),
            chunks=len(chunks),
        )

        return chunks

    def _infer_source_type(self, filename: str) -> str:
        extension = filename.split(".")[-1].lower()
        type_mapping = {
            "pdf": "document",
            "mp3": "audio",
            "wav": "audio",
            "csv": "spreadsheet",
            "xlsx": "spreadsheet",
            "xls": "spreadsheet",
        }
        return type_mapping.get(extension, "unknown")
