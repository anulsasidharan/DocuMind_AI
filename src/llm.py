"""Chat LLM factory."""

from langchain_openai import ChatOpenAI

from src.config import Settings, get_settings


def get_llm(settings: Settings | None = None) -> ChatOpenAI:
    s = settings or get_settings()
    return ChatOpenAI(
        model=s.llm_model,
        temperature=s.temperature,
        max_tokens=s.max_tokens,
    )
