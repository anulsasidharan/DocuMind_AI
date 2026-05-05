"""Unit tests for chunking and loaders (no network)."""

from langchain_core.documents import Document

from pipelines.components.chunker import get_text_splitter
from pipelines.components.loader import load_text_files
from src.config import Settings


def test_chunk_splitter_respects_overlap():
    s = Settings().model_copy(update={"chunk_size": 100, "chunk_overlap": 20})
    splitter = get_text_splitter(s)
    doc = Document(page_content="x" * 500)
    chunks = splitter.split_documents([doc])
    assert len(chunks) > 1


def test_load_text_files_handles_string_path(tmp_path):
    f = tmp_path / "sample.md"
    f.write_text("# Hello\n\nWorld.", encoding="utf-8")
    docs = load_text_files([str(f)])
    assert len(docs) == 1
    assert "Hello" in docs[0].page_content
