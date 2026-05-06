"""Qdrant vector store and base retriever."""

from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from src.config import Settings, get_settings
from src.embeddings import get_embeddings


def get_qdrant_client(settings: Settings | None = None) -> QdrantClient:
    s = settings or get_settings()
    kwargs: dict = {"url": s.qdrant_url}
    if s.qdrant_api_key:
        kwargs["api_key"] = s.qdrant_api_key
    return QdrantClient(**kwargs)


def _ensure_collection(client: QdrantClient, settings: Settings) -> None:
    """Create the collection with the correct vector schema if it doesn't exist."""
    existing = {c.name for c in client.get_collections().collections}
    if settings.collection_name not in existing:
        client.create_collection(
            collection_name=settings.collection_name,
            vectors_config=VectorParams(
                size=settings.embedding_dimensions,
                distance=Distance.COSINE,
            ),
        )


def get_vector_store(settings: Settings | None = None) -> QdrantVectorStore:
    s = settings or get_settings()
    client = get_qdrant_client(s)
    _ensure_collection(client, s)
    embeddings = get_embeddings(s)
    return QdrantVectorStore(
        client=client,
        collection_name=s.collection_name,
        embedding=embeddings,
    )


def get_base_retriever(settings: Settings | None = None):
    s = settings or get_settings()
    vs = get_vector_store(s)
    return vs.as_retriever(
        search_type="similarity",
        search_kwargs={"k": s.top_k},
    )
