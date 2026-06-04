from app.core.exceptions import IngestionError
from app.core.providers.transcription import TranscriptionProvider
from app.utils.logging import get_logger

logger = get_logger(__name__)


class AudioParser:
    def __init__(self, transcription_provider: TranscriptionProvider) -> None:
        self.transcription_provider = transcription_provider

    async def parse(self, file_path: str) -> list[dict[str, str | int]]:
        try:
            transcript = await self.transcription_provider.transcribe(file_path)

            if not transcript.strip():
                raise IngestionError("No transcript generated from audio file")

            logger.info("audio_transcribed", file_path=file_path, length=len(transcript))

            return [{"page": None, "content": transcript.strip()}]

        except Exception as e:
            logger.error("audio_parse_failed", error=str(e), file_path=file_path)
            raise IngestionError(f"Failed to parse audio: {str(e)}")
