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
    """Create the collection (if absent) and ensure the doc_id payload index exists."""
    existing = {c.name for c in client.get_collections().collections}
    if settings.collection_name not in existing:
        client.create_collection(
            collection_name=settings.collection_name,
            vectors_config=VectorParams(
                size=settings.embedding_dimensions,
                distance=Distance.COSINE,
            ),
        )
    # Payload index on metadata.doc_id is required for filtered similarity search.
    # The call is idempotent — safe to run even when the index already exists.
    try:
        from qdrant_client.models import PayloadSchemaType

        client.create_payload_index(
            collection_name=settings.collection_name,
            field_name="metadata.doc_id",
            field_schema=PayloadSchemaType.KEYWORD,
        )
    except Exception:
        pass


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


def get_base_retriever(
    settings: Settings | None = None,
    doc_ids: list[str] | None = None,
):
    """Return a similarity retriever, optionally filtered to specific doc_ids."""
    s = settings or get_settings()
    vs = get_vector_store(s)
    search_kwargs: dict = {"k": s.top_k}
    if doc_ids:
        from qdrant_client.models import FieldCondition, Filter, MatchAny

        search_kwargs["filter"] = Filter(
            must=[
                FieldCondition(
                    key="metadata.doc_id",
                    match=MatchAny(any=list(doc_ids)),
                )
            ]
        )
    return vs.as_retriever(search_type="similarity", search_kwargs=search_kwargs)
