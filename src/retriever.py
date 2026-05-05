"""Qdrant vector store and base retriever."""

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from src.config import Settings, get_settings
from src.embeddings import get_embeddings


def get_qdrant_client(settings: Settings | None = None) -> QdrantClient:
    s = settings or get_settings()
    kwargs: dict = {"url": s.qdrant_url}
    if s.qdrant_api_key:
        kwargs["api_key"] = s.qdrant_api_key
    return QdrantClient(**kwargs)


def get_vector_store(settings: Settings | None = None) -> QdrantVectorStore:
    s = settings or get_settings()
    client = get_qdrant_client(s)
    embeddings = get_embeddings(s)
    return QdrantVectorStore(
        client=client,
        collection_name=s.collection_name,
        embedding=embeddings,
        distance="COSINE",
    )


def get_base_retriever(settings: Settings | None = None):
    s = settings or get_settings()
    vs = get_vector_store(s)
    return vs.as_retriever(
        search_type="similarity",
        search_kwargs={"k": s.top_k},
    )
