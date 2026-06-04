from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "AidOps AI"
    app_version: str = "1.0.0"
    environment: Literal["development", "production"] = "development"
    debug: bool = True
    log_level: str = "INFO"

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = True

    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"]
    )
    cors_allow_credentials: bool = True

    database_url: str = "sqlite:///./aidops.db"

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = ""
    redis_cache_ttl: int = 3600

    llm_provider: Literal["openai", "anthropic", "mock"] = "mock"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000

    use_litellm: bool = False
    litellm_api_base: str = ""

    embedding_provider: Literal["openai", "local"] = "local"
    openai_embedding_model: str = "text-embedding-3-small"
    local_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    vector_db_provider: Literal["pinecone", "faiss", "chroma"] = "faiss"
    pinecone_api_key: str = ""
    pinecone_environment: str = ""
    pinecone_index_name: str = "aidops-ai"
    vector_db_dimension: int = 384

    transcription_provider: Literal["openai", "local"] = "local"
    whisper_model: str = "base"

    news_api_key: str = ""
    weather_api_key: str = ""
    feed_poll_interval: int = 300

    chunk_size: int = 500
    chunk_overlap: int = 50
    retrieval_top_k: int = 5
    retrieval_score_threshold: float = 0.3  # Lowered for better recall in demo mode
    use_hybrid_search: bool = True
    use_reranking: bool = False

    secret_key: str = "your-secret-key-change-this-in-production"
    rate_limit_per_minute: int = 60
    max_upload_size_mb: int = 50
    allowed_file_types: list[str] = Field(
        default_factory=lambda: ["pdf", "mp3", "wav", "csv", "xlsx"]
    )

    enable_tracing: bool = True
    langsmith_api_key: str = ""
    langsmith_project: str = "aidops-ai"
    enable_token_tracking: bool = True

    upload_dir: str = "./uploads"
    sample_data_dir: str = "./data/sample"

    agent_max_iterations: int = 10
    agent_timeout_seconds: int = 120

    force_demo_mode: bool = False

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("allowed_file_types", mode="before")
    @classmethod
    def parse_allowed_file_types(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [ft.strip() for ft in v.split(",")]
        return v

    @property
    def is_demo_mode(self) -> bool:
        if self.force_demo_mode:
            return True
        return not self.openai_api_key and not self.anthropic_api_key

    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
