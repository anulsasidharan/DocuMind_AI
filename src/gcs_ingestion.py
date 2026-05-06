"""Helpers for uploading documents to GCS and indexing them."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from google.cloud import storage

from src.config import Settings, get_settings
from src.rag_pipeline import index_documents


def _safe_filename(filename: str) -> str:
    return Path(filename).name.replace("\\", "_").replace("/", "_")


def upload_bytes_to_gcs(
    *,
    file_bytes: bytes,
    filename: str,
    content_type: str | None = None,
    settings: Settings | None = None,
) -> str | None:
    """Upload bytes to the configured GCS docs bucket and return gs:// URI.

    Returns None if GCS is not configured or credentials are unavailable.
    """
    import logging

    s = settings or get_settings()
    if not s.gcs_bucket_docs:
        logging.warning("GCS upload skipped: GCS_BUCKET_DOCS is not configured.")
        return None

    try:
        client = storage.Client(project=s.gcp_project_id or None)
        bucket = client.bucket(s.gcs_bucket_docs)
        ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        object_name = f"raw/uploads/{ts}-{_safe_filename(filename)}"
        blob = bucket.blob(object_name)
        blob.upload_from_string(file_bytes, content_type=content_type or "application/octet-stream")
        return f"gs://{s.gcs_bucket_docs}/{object_name}"
    except Exception as exc:
        logging.warning("GCS upload skipped (credentials unavailable): %s", exc)
        return None


def index_uploaded_bytes(
    *,
    file_bytes: bytes,
    filename: str,
    settings: Settings | None = None,
) -> int:
    """Persist uploaded bytes as temp file and index into vector store."""
    s = settings or get_settings()
    suffix = Path(filename).suffix or ".txt"
    with TemporaryDirectory() as tmp:
        local_path = Path(tmp) / f"upload{suffix}"
        local_path.write_bytes(file_bytes)
        return index_documents([str(local_path)], settings=s)
