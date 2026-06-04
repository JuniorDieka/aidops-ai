from pathlib import Path

import fitz

from app.core.exceptions import IngestionError
from app.utils.logging import get_logger

logger = get_logger(__name__)


class PDFParser:
    async def parse(self, file_path: str) -> list[dict[str, str | int]]:
        try:
            return await self._parse_pdf(file_path)
        except Exception as e:
            logger.error("pdf_parse_failed", error=str(e), file_path=file_path)
            raise IngestionError(f"Failed to parse PDF: {str(e)}")

    async def _parse_pdf(self, file_path: str) -> list[dict[str, str | int]]:
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._parse_pdf_sync, file_path)

    def _parse_pdf_sync(self, file_path: str) -> list[dict[str, str | int]]:
        doc = fitz.open(file_path)
        pages = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()

            if text.strip():
                pages.append({"page": page_num + 1, "content": text.strip()})

        doc.close()

        if not pages:
            raise IngestionError("No text content found in PDF")

        logger.info("pdf_parsed", file_path=file_path, pages=len(pages))
        return pages
