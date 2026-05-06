"""Document loading for indexing (multi-format)."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, List

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    BSHTMLLoader,
    CSVLoader,
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)


SUPPORTED_EXTS = {".md", ".txt", ".pdf", ".html", ".htm", ".docx", ".csv", ".json"}


def _iter_files(paths: Iterable[str | Path]) -> Iterable[Path]:
    for raw in paths:
        p = Path(raw)
        if p.is_file():
            yield p
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                if f.is_file():
                    yield f


def _load_json(path: Path) -> List[Document]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        text = json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        # Fallback to raw text if invalid JSON or encoding issues
        text = path.read_text(errors="ignore")
    return [Document(page_content=text, metadata={"source": str(path)})]


def _load_csv(path: Path) -> List[Document]:
    """
    Prefer CSVLoader when possible; if it fails, fallback to a simple csv->text rendering.
    """
    try:
        return CSVLoader(file_path=str(path), encoding="utf-8").load()
    except Exception:
        rows: list[list[str]] = []
        with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                rows.append(row)
                if i >= 5000:
                    break
        rendered = "\n".join([", ".join(r) for r in rows])
        return [Document(page_content=rendered, metadata={"source": str(path)})]


def load_documents(paths: List[str | Path], encoding: str = "utf-8") -> List[Document]:
    """Load .pdf/.md/.txt/.html/.docx/.csv/.json documents as LangChain Documents."""
    docs: List[Document] = []
    for path in _iter_files(paths):
        ext = path.suffix.lower()
        if ext not in SUPPORTED_EXTS:
            continue

        if ext in {".md", ".txt"}:
            docs.extend(TextLoader(str(path), encoding=encoding).load())
        elif ext == ".pdf":
            docs.extend(PyPDFLoader(str(path)).load())
        elif ext in {".html", ".htm"}:
            docs.extend(BSHTMLLoader(str(path), open_encoding=encoding).load())
        elif ext == ".docx":
            docs.extend(Docx2txtLoader(str(path)).load())
        elif ext == ".csv":
            docs.extend(_load_csv(path))
        elif ext == ".json":
            docs.extend(_load_json(path))

    return docs
