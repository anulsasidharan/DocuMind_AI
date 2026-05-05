"""OpenAI embedding factory."""

from langchain_openai import OpenAIEmbeddings

from src.config import Settings, get_settings


def get_embeddings(settings: Settings | None = None) -> OpenAIEmbeddings:
    s = settings or get_settings()
    return OpenAIEmbeddings(model=s.embedding_model)
