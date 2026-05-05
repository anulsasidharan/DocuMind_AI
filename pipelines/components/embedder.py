"""Embedding utilities for batch indexing (shared OpenAI client)."""

from langchain_openai import OpenAIEmbeddings

from src.embeddings import get_embeddings


def get_pipeline_embeddings() -> OpenAIEmbeddings:
    return get_embeddings()
