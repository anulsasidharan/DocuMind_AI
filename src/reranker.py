"""Cross-encoder reranking on top of a base retriever."""

from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

from src.config import Settings, get_settings
from src.retriever import get_base_retriever

# Cache loaded cross-encoder models — downloading/loading is expensive.
_model_cache: dict[str, HuggingFaceCrossEncoder] = {}


def _get_cross_encoder(model_name: str) -> HuggingFaceCrossEncoder:
    if model_name not in _model_cache:
        _model_cache[model_name] = HuggingFaceCrossEncoder(model_name=model_name)
    return _model_cache[model_name]


def get_reranked_retriever(
    settings: Settings | None = None,
    doc_ids: list[str] | None = None,
):
    """Wraps dense similarity retriever with a cached HuggingFace cross-encoder.

    Pass doc_ids to restrict retrieval to specific indexed documents.
    For production Cohere rerank, replace compressor with a Cohere-based one.
    """
    s = settings or get_settings()
    base = get_base_retriever(s, doc_ids=doc_ids)
    model = _get_cross_encoder(s.cross_encoder_model)
    compressor = CrossEncoderReranker(model=model, top_n=s.rerank_top_n)
    return ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base,
    )
