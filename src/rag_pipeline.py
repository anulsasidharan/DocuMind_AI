"""RAG chain: retrieval, prompt, optional chat history, indexing."""

from operator import itemgetter
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
from src.retriever import get_vector_store
from src.reranker import get_reranked_retriever
from pipelines.components.chunker import get_text_splitter
from pipelines.components.loader import load_text_files


def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(
    *,
    llm: ChatOpenAI | None = None,
    settings: Settings | None = None,
):
    s = settings or get_settings()
    retriever = get_reranked_retriever(s)
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


_rag_with_history_default = None


def get_rag_chain_with_history(settings: Settings | None = None):
    """Returns chain with chat history; default instance is reused (loads reranker once)."""
    global _rag_with_history_default
    if settings is not None:
        inner = build_rag_chain(settings=settings)
        return RunnableWithMessageHistory(
            inner,
            get_session_history,
            input_messages_key="question",
            history_messages_key="chat_history",
        )
    if _rag_with_history_default is None:
        s = get_settings()
        inner = build_rag_chain(settings=s)
        _rag_with_history_default = RunnableWithMessageHistory(
            inner,
            get_session_history,
            input_messages_key="question",
            history_messages_key="chat_history",
        )
    return _rag_with_history_default


def index_documents(
    file_paths: List[str],
    settings: Settings | None = None,
) -> int:
    """Load, chunk, embed, and upsert into Qdrant. Returns chunk count."""
    s = settings or get_settings()
    all_docs = load_text_files(file_paths)
    if not all_docs:
        return 0
    splitter = get_text_splitter(s)
    chunks = splitter.split_documents(all_docs)
    vs = get_vector_store(s)
    vs.add_documents(chunks)
    return len(chunks)


def query(question: str, session_id: str = "default", settings: Settings | None = None) -> str:
    """Run a RAG query and return the generated answer."""
    s = settings or get_settings()
    rag = get_rag_chain_with_history(s)
    return rag.invoke(
        {"question": question},
        config={"configurable": {"session_id": session_id}},
    )
