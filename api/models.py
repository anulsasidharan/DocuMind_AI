"""Pydantic API schemas."""

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    session_id: str = Field(default="default")


class QueryResponse(BaseModel):
    answer: str
    session_id: str


class UploadResponse(BaseModel):
    filename: str
    chunks_indexed: int
    gcs_uri: str | None = None


class UploadQueryResponse(BaseModel):
    answer: str
    session_id: str
    gcs_uri: str | None = None
    chunks_indexed: int


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "documind-api"
