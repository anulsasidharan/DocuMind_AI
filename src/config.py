"""Application settings (env + defaults)."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    cloud_provider: str = "gcp"
    collection_name: str = Field(default="docs-index", validation_alias="COLLECTION_NAME")

    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    qdrant_url: str = Field(default="http://localhost:6333", validation_alias="QDRANT_URL")
    qdrant_api_key: str | None = Field(default=None, validation_alias="QDRANT_API_KEY")

    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    llm_model: str = "gpt-4o"
    temperature: float = 0.1
    max_tokens: int = 2048

    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 8
    rerank_top_n: int = 5

    # Hugging Face cross-encoder (used by CrossEncoderReranker). For Cohere rerank, swap reranker module later.
    cross_encoder_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        validation_alias="CROSS_ENCODER_MODEL",
    )

    memory_window_k: int = 10

    gcp_project_id: str | None = Field(default=None, validation_alias="GCP_PROJECT_ID")
    gcs_bucket_docs: str | None = Field(default=None, validation_alias="GCS_BUCKET_DOCS")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")


@lru_cache
def get_settings() -> Settings:
    return Settings()
