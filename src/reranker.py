"""Cross-encoder reranking on top of a base retriever."""

from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder

from src.config import Settings, get_settings
from src.retriever import get_base_retriever


def get_reranked_retriever(settings: Settings | None = None):
    """
    Wraps dense similarity retriever with a HuggingFace cross-encoder reranker.
    For production Cohere rerank, replace with a Cohere-based compressor.
    """
    s = settings or get_settings()
    base = get_base_retriever(s)
    model = HuggingFaceCrossEncoder(model_name=s.cross_encoder_model)
    compressor = CrossEncoderReranker(model=model, top_n=s.rerank_top_n)
    return ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base,
    )
