"""FastAPI entrypoint."""

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
