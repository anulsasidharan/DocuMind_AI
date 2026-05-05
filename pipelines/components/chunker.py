"""Text splitting for indexing."""

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import Settings, get_settings


def get_text_splitter(settings: Settings | None = None) -> RecursiveCharacterTextSplitter:
    s = settings or get_settings()
    return RecursiveCharacterTextSplitter(
        chunk_size=s.chunk_size,
        chunk_overlap=s.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
