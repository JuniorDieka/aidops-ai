from abc import ABC, abstractmethod
from pathlib import Path


class TranscriptionProvider(ABC):
    @abstractmethod
    async def transcribe(self, audio_file_path: str) -> str:
        pass


class OpenAITranscriptionProvider(TranscriptionProvider):
    def __init__(self, api_key: str) -> None:
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=api_key)

    async def transcribe(self, audio_file_path: str) -> str:
        with open(audio_file_path, "rb") as audio_file:
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )
        return transcript.text


class LocalTranscriptionProvider(TranscriptionProvider):
    def __init__(self, model_size: str = "base") -> None:
        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        except (ImportError, ModuleNotFoundError):
            self.model = None

    async def transcribe(self, audio_file_path: str) -> str:
        if self.model is None:
            return "[Audio transcription unavailable - faster_whisper not installed]"
        
        import asyncio

        loop = asyncio.get_event_loop()
        segments, _ = await loop.run_in_executor(None, self.model.transcribe, audio_file_path)

        transcript_parts = []
        for segment in segments:
            transcript_parts.append(segment.text)

        return " ".join(transcript_parts)


class MockTranscriptionProvider(TranscriptionProvider):
    async def transcribe(self, audio_file_path: str) -> str:
        return f"[Mock transcription of {Path(audio_file_path).name}] This is a simulated transcript for demo purposes."
