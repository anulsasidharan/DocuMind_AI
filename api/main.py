"""FastAPI entrypoint."""

from pathlib import Path
from dotenv import load_dotenv

# Resolve .env from the project root regardless of the working directory.
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)

from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title="DocuMind AI",
    description="Documentation RAG API",
    version="0.1.0",
)
app.include_router(router)


@app.get("/")
def root() -> dict:
    return {"service": "documind-api", "docs": "/docs"}
