"""RAG pipeline tests (structure only; full flow needs keys + Qdrant)."""

import pytest


@pytest.mark.skip(reason="Requires OPENAI_API_KEY, QDRANT_URL, indexed collection")
def test_query_integration():
    from src.rag_pipeline import query

    _ = query("What is Vertex AI?", session_id="test")
