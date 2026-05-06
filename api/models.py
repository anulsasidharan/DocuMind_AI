"""Pydantic API schemas."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    session_id: str = Field(default="default")
    doc_ids: list[str] | None = Field(
        default=None,
        description="Restrict retrieval to these doc IDs. Omit or pass null to query all documents.",
    )


class QueryResponse(BaseModel):
    answer: str
    session_id: str


class DocumentInfo(BaseModel):
    doc_id: str
    filename: str
    chunk_count: int


class UploadResponse(BaseModel):
    filename: str
    doc_id: str
    chunks_indexed: int
    gcs_uri: str | None = None


class UploadQueryResponse(BaseModel):
    answer: str
    session_id: str
    doc_id: str
    gcs_uri: str | None = None
    chunks_indexed: int


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "documind-api"
