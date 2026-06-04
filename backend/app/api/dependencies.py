from functools import lru_cache

from app.agents.workflows import WorkflowOrchestrator
from app.config import settings
from app.core.providers.embeddings import EmbeddingProvider, LocalEmbeddingProvider, OpenAIEmbeddingProvider
from app.core.providers.external_feeds import ExternalFeed, MockNewsFeed, MockWeatherFeed, RealNewsFeed
from app.core.providers.llm import AnthropicLLMProvider, LLMProvider, MockLLMProvider, OpenAILLMProvider
from app.core.providers.transcription import LocalTranscriptionProvider, MockTranscriptionProvider, OpenAITranscriptionProvider, TranscriptionProvider
from app.core.providers.vectorstore import FAISSVectorStore, PineconeVectorStore, VectorStoreProvider
from app.services.cache import cache_service
from app.services.chat.session import ChatSessionManager
from app.services.chat.streaming import StreamingChatService
from app.services.ingestion.audio_parser import AudioParser
from app.services.ingestion.chunker import DocumentChunker
from app.services.ingestion.pdf_parser import PDFParser
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.ingestion.spreadsheet_parser import SpreadsheetParser
from app.services.retrieval.retriever import RAGRetriever


@lru_cache()
def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "openai" and settings.openai_api_key:
        return OpenAILLMProvider(api_key=settings.openai_api_key, model=settings.llm_model)
    elif settings.llm_provider == "anthropic" and settings.anthropic_api_key:
        return AnthropicLLMProvider(api_key=settings.anthropic_api_key, model=settings.llm_model)
    else:
        return MockLLMProvider()


@lru_cache()
def get_embedding_provider() -> EmbeddingProvider:
    if settings.embedding_provider == "openai" and settings.openai_api_key:
        return OpenAIEmbeddingProvider(
            api_key=settings.openai_api_key, model=settings.openai_embedding_model
        )
    else:
        return LocalEmbeddingProvider(model_name=settings.local_embedding_model)


@lru_cache()
def get_vector_store() -> VectorStoreProvider:
    embedding_provider = get_embedding_provider()
    dimension = embedding_provider.dimension()

    if settings.vector_db_provider == "pinecone" and settings.pinecone_api_key:
        return PineconeVectorStore(
            api_key=settings.pinecone_api_key,
            environment=settings.pinecone_environment,
            index_name=settings.pinecone_index_name,
        )
    else:
        return FAISSVectorStore(dimension=dimension)


@lru_cache()
def get_transcription_provider() -> TranscriptionProvider:
    if settings.transcription_provider == "openai" and settings.openai_api_key:
        return OpenAITranscriptionProvider(api_key=settings.openai_api_key)
    else:
        # Use mock provider in demo mode to avoid faster_whisper dependency
        try:
            return LocalTranscriptionProvider(model_size=settings.whisper_model)
        except (ImportError, ModuleNotFoundError):
            return MockTranscriptionProvider()


@lru_cache()
def get_news_feed() -> ExternalFeed:
    if settings.news_api_key:
        return RealNewsFeed(api_key=settings.news_api_key)
    else:
        return MockNewsFeed()


@lru_cache()
def get_weather_feed() -> ExternalFeed:
    return MockWeatherFeed()


def get_retriever() -> RAGRetriever:
    return RAGRetriever(
        embedding_provider=get_embedding_provider(),
        vector_store=get_vector_store(),
    )


def get_ingestion_pipeline() -> IngestionPipeline:
    return IngestionPipeline(
        pdf_parser=PDFParser(),
        audio_parser=AudioParser(transcription_provider=get_transcription_provider()),
        spreadsheet_parser=SpreadsheetParser(),
        chunker=DocumentChunker(),
        embedding_provider=get_embedding_provider(),
        vector_store=get_vector_store(),
    )


def get_chat_session_manager() -> ChatSessionManager:
    return ChatSessionManager(cache_service=cache_service)


def get_streaming_chat_service() -> StreamingChatService:
    return StreamingChatService(
        llm_provider=get_llm_provider(),
        retriever=get_retriever(),
    )


def get_workflow_orchestrator() -> WorkflowOrchestrator:
    return WorkflowOrchestrator(
        retriever=get_retriever(),
        news_feed=get_news_feed(),
        weather_feed=get_weather_feed(),
    )
