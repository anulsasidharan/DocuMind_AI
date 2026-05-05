"""Document loading for indexing."""

from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader


def load_text_files(paths: List[str | Path], encoding: str = "utf-8") -> List[Document]:
    """Load plain text / markdown files as LangChain documents."""
    docs: List[Document] = []
    for raw in paths:
        path = Path(raw)
        if path.is_file():
            loader = TextLoader(str(path), encoding=encoding)
            docs.extend(loader.load())
        elif path.is_dir():
            for f in sorted(path.rglob("*.md")):
                loader = TextLoader(str(f), encoding=encoding)
                docs.extend(loader.load())
            for f in sorted(path.rglob("*.txt")):
                loader = TextLoader(str(f), encoding=encoding)
                docs.extend(loader.load())
    return docs
