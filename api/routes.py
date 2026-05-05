"""API route handlers (mounted from main)."""

from fastapi import APIRouter, HTTPException

from api.models import HealthResponse, QueryRequest, QueryResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@router.post("/api/v1/query", response_model=QueryResponse)
def post_query(body: QueryRequest) -> QueryResponse:
    try:
        from src.rag_pipeline import query as rag_query

        answer = rag_query(body.question, session_id=body.session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return QueryResponse(answer=answer, session_id=body.session_id)
