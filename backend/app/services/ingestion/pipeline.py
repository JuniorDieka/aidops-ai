from pathlib import Path

from app.config import settings
from app.core.exceptions import IngestionError
from app.core.models import DocumentChunk, FileType, IngestionJob, IngestionStatus
from app.core.providers.embeddings import EmbeddingProvider
from app.core.providers.vectorstore import VectorStoreProvider
from app.services.ingestion.audio_parser import AudioParser
from app.services.ingestion.chunker import DocumentChunker
from app.services.ingestion.pdf_parser import PDFParser
from app.services.ingestion.spreadsheet_parser import SpreadsheetParser
from app.utils.logging import get_logger

logger = get_logger(__name__)


class IngestionPipeline:
    def __init__(
        self,
        pdf_parser: PDFParser,
        audio_parser: AudioParser,
        spreadsheet_parser: SpreadsheetParser,
        chunker: DocumentChunker,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStoreProvider,
    ) -> None:
        self.pdf_parser = pdf_parser
        self.audio_parser = audio_parser
        self.spreadsheet_parser = spreadsheet_parser
        self.chunker = chunker
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store

    async def ingest_file(self, file_path: str, file_type: FileType) -> IngestionJob:
        job = IngestionJob(
            file_name=Path(file_path).name,
            file_type=file_type,
            status=IngestionStatus.PROCESSING,
        )

        try:
            logger.info("ingestion_started", file_path=file_path, file_type=file_type.value)

            if file_type == FileType.PDF:
                pages = await self.pdf_parser.parse(file_path)
            elif file_type == FileType.AUDIO:
                pages = await self.audio_parser.parse(file_path)
            elif file_type == FileType.SPREADSHEET:
                pages = await self.spreadsheet_parser.parse(file_path)
            else:
                raise IngestionError(f"Unsupported file type: {file_type}")

            chunks = await self.chunker.chunk_documents(pages, Path(file_path).name)

            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = await self.embedding_provider.embed_batch(chunk_texts)

            for chunk, embedding in zip(chunks, embeddings):
                chunk.embedding = embedding

            await self.vector_store.add_chunks(chunks)

            job.status = IngestionStatus.COMPLETED
            job.chunks_created = len(chunks)

            logger.info(
                "ingestion_completed",
                file_path=file_path,
                chunks=len(chunks),
            )

            return job

        except Exception as e:
            logger.error("ingestion_failed", file_path=file_path, error=str(e))
            job.status = IngestionStatus.FAILED
            job.error_message = str(e)
            return job
