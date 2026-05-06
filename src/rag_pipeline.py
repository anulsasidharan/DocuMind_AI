"""RAG chain: retrieval, prompt, optional chat history, indexing, document listing."""

import uuid as _uuid
from operator import itemgetter
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_openai import ChatOpenAI

from src.config import Settings, get_settings
from src.llm import get_llm
from src.retriever import get_qdrant_client, get_vector_store
from src.reranker import get_reranked_retriever
from pipelines.components.chunker import get_text_splitter
from pipelines.components.loader import load_documents


def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(
    *,
    llm: ChatOpenAI | None = None,
    settings: Settings | None = None,
    doc_ids: list[str] | None = None,
):
    s = settings or get_settings()
    retriever = get_reranked_retriever(s, doc_ids=doc_ids)
    model = llm or get_llm(s)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a technical documentation assistant. Answer questions accurately based on the provided documentation context. Include code examples when relevant. Always cite the source section. If the information is not in the context, say so.

Context:
{context}

Format your answer using Markdown.""",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    return (
        RunnableParallel(
            {
                "context": itemgetter("question") | retriever | format_docs,
                "question": itemgetter("question"),
                "chat_history": itemgetter("chat_history"),
            }
        )
        | prompt
        | model
        | StrOutputParser()
    )


_store: dict[str, BaseChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in _store:
        _store[session_id] = InMemoryChatMessageHistory()
    return _store[session_id]


def clear_session_history(session_id: str) -> None:
    """Remove conversation history for a session (call when switching doc scope)."""
    _store.pop(session_id, None)


def index_documents(
    file_paths: List[str],
    settings: Settings | None = None,
    doc_id: str | None = None,
    source_name: str | None = None,
) -> tuple[int, str]:
    """Load, chunk, embed, and upsert into Qdrant.

    Stamps every chunk with ``doc_id`` (and the human-readable ``source_name``
    if supplied) so it can be retrieved in isolation later.
    Returns (chunk_count, doc_id).
    """
    s = settings or get_settings()
    _doc_id = doc_id or str(_uuid.uuid4())
    all_docs = load_documents(file_paths)
    if not all_docs:
        return 0, _doc_id
    splitter = get_text_splitter(s)
    chunks = splitter.split_documents(all_docs)
    for chunk in chunks:
        chunk.metadata["doc_id"] = _doc_id
        if source_name:
            chunk.metadata["source"] = source_name
    vs = get_vector_store(s)
    vs.add_documents(chunks)
    return len(chunks), _doc_id


def get_indexed_documents(settings: Settings | None = None) -> list[dict]:
    """Return [{doc_id, filename, chunk_count}] for every document in the collection."""
    s = settings or get_settings()
    client = get_qdrant_client(s)

    # Collection might not exist yet on a fresh deployment — return empty list.
    existing = {c.name for c in client.get_collections().collections}
    if s.collection_name not in existing:
        return []

    # Scroll the whole collection and aggregate by doc_id.
    docs: dict[str, dict] = {}
    offset = None
    while True:
        result, next_offset = client.scroll(
            collection_name=s.collection_name,
            limit=200,
            with_payload=True,
            with_vectors=False,
            offset=offset,
        )
        for point in result:
            metadata = (point.payload or {}).get("metadata", {})
            doc_id = metadata.get("doc_id")
            if not doc_id:
                continue
            source = metadata.get("source", "")
            filename = Path(source).name if source else "unknown"
            entry = docs.setdefault(doc_id, {"doc_id": doc_id, "filename": filename, "chunk_count": 0})
            entry["chunk_count"] += 1
        if next_offset is None:
            break
        offset = next_offset

    return sorted(docs.values(), key=lambda d: d["filename"])


def query(
    question: str,
    session_id: str = "default",
    settings: Settings | None = None,
    doc_ids: list[str] | None = None,
) -> str:
    """Run a RAG query and return the generated answer.

    Pass doc_ids to restrict context to specific indexed documents.
    """
    s = settings or get_settings()
    chain = build_rag_chain(settings=s, doc_ids=doc_ids)
    rag_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history",
    )
    return rag_with_history.invoke(
        {"question": question},
        config={"configurable": {"session_id": session_id}},
    )
