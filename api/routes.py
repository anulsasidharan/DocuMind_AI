"""API route handlers (mounted from main)."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from api.models import HealthResponse, QueryRequest, QueryResponse, UploadQueryResponse, UploadResponse

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
        chunks = index_uploaded_bytes(file_bytes=raw, filename=filename)
        return UploadResponse(filename=filename, chunks_indexed=chunks, gcs_uri=gcs_uri)
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
    """Upload a document, index it into Qdrant, then answer a question about it."""
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
        chunks = index_uploaded_bytes(file_bytes=raw, filename=filename)
        answer = rag_query(question, session_id=session_id)
        return UploadQueryResponse(
            answer=answer,
            session_id=session_id,
            gcs_uri=gcs_uri,
            chunks_indexed=chunks,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
