"""API route handlers."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.models import (
    DocumentInfo,
    HealthResponse,
    QueryRequest,
    QueryResponse,
    UploadQueryResponse,
    UploadResponse,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@router.get("/api/v1/documents", response_model=list[DocumentInfo])
def list_documents() -> list[DocumentInfo]:
    """Return every document that has been indexed into Qdrant."""
    try:
        from src.rag_pipeline import get_indexed_documents

        return [DocumentInfo(**d) for d in get_indexed_documents()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/api/v1/query", response_model=QueryResponse)
def post_query(body: QueryRequest) -> QueryResponse:
    try:
        from src.rag_pipeline import query as rag_query

        answer = rag_query(
            body.question,
            session_id=body.session_id,
            doc_ids=body.doc_ids or None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return QueryResponse(answer=answer, session_id=body.session_id)


@router.post("/api/v1/clear-session")
def clear_session(session_id: str) -> dict:
    """Wipe conversation history for a session (call when the doc scope changes)."""
    try:
        from src.rag_pipeline import clear_session_history

        clear_session_history(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return {"cleared": True, "session_id": session_id}


@router.post("/api/v1/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    """Upload a document to GCS (if configured) and index it into Qdrant."""
    try:
        from src.gcs_ingestion import index_uploaded_bytes, upload_bytes_to_gcs

        raw = await file.read()
        if not raw:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        filename = file.filename or "uploaded.bin"
        gcs_uri = upload_bytes_to_gcs(
            file_bytes=raw,
            filename=filename,
            content_type=file.content_type,
        )
        chunks, doc_id = index_uploaded_bytes(file_bytes=raw, filename=filename)
        return UploadResponse(
            filename=filename,
            doc_id=doc_id,
            chunks_indexed=chunks,
            gcs_uri=gcs_uri,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/api/v1/upload-query", response_model=UploadQueryResponse)
async def upload_and_query(
    file: UploadFile = File(...),
    question: str = Form(...),
    session_id: str = Form("default"),
) -> UploadQueryResponse:
    """Upload a document, index it, then answer a question scoped to that document."""
    try:
        from src.gcs_ingestion import index_uploaded_bytes, upload_bytes_to_gcs
        from src.rag_pipeline import query as rag_query

        raw = await file.read()
        if not raw:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        filename = file.filename or "uploaded.bin"
        gcs_uri = upload_bytes_to_gcs(
            file_bytes=raw,
            filename=filename,
            content_type=file.content_type,
        )
        chunks, doc_id = index_uploaded_bytes(file_bytes=raw, filename=filename)
        answer = rag_query(question, session_id=session_id, doc_ids=[doc_id])
        return UploadQueryResponse(
            answer=answer,
            session_id=session_id,
            doc_id=doc_id,
            gcs_uri=gcs_uri,
            chunks_indexed=chunks,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
