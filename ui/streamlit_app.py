"""Streamlit chat UI for DocuMind AI — with per-document scoping."""

from __future__ import annotations

import os
import uuid

import httpx
import streamlit as st

API_URL = os.environ.get("DOCUMIND_API_URL", "http://127.0.0.1:8001")
_TIMEOUT_UPLOAD = 300
_TIMEOUT_QUERY = 120
_TIMEOUT_SHORT = 5


# ── helpers ──────────────────────────────────────────────────────────────────

def _get(path: str, **kw) -> httpx.Response:
    return httpx.get(f"{API_URL}{path}", timeout=_TIMEOUT_SHORT, **kw)


def _post(path: str, **kw) -> httpx.Response:
    return httpx.post(f"{API_URL}{path}", **kw)


def fetch_indexed_docs() -> list[dict]:
    """Pull the live document list from Qdrant via the API."""
    try:
        r = _get("/api/v1/documents")
        r.raise_for_status()
        return r.json()  # [{doc_id, filename, chunk_count}, ...]
    except Exception:
        return []


def clear_session_on_server(session_id: str) -> None:
    try:
        _post(f"/api/v1/clear-session?session_id={session_id}", timeout=_TIMEOUT_SHORT)
    except Exception:
        pass


# ── page config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="DocuMind AI", page_icon="📚", layout="wide")

# ── session state bootstrap ───────────────────────────────────────────────────

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
# doc_ids=None means "query all"; a list means "query only these"
if "selected_doc_ids" not in st.session_state:
    st.session_state.selected_doc_ids: list[str] | None = None
# Full list fetched from API (refreshed on upload and on load)
if "indexed_docs" not in st.session_state:
    st.session_state.indexed_docs: list[dict] = fetch_indexed_docs()
if "scope_mode" not in st.session_state:
    # "all" or "selected"
    st.session_state.scope_mode = "all"


def _refresh_docs() -> None:
    st.session_state.indexed_docs = fetch_indexed_docs()


def _reset_conversation() -> None:
    clear_session_on_server(st.session_state.session_id)
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())[:8]


def _effective_doc_ids() -> list[str] | None:
    """Return doc_ids to send in the query, or None for 'all'."""
    if st.session_state.scope_mode == "all":
        return None
    return st.session_state.selected_doc_ids or None


# ── sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("📚 DocuMind AI")
    st.caption("Intelligent Documentation Q&A")

    # — API health ————————————————————————————————————————————————————————————
    try:
        hr = _get("/health")
        if hr.status_code == 200:
            st.success("API connected", icon="✅")
        else:
            st.warning("API returned non-200", icon="⚠️")
    except Exception:
        st.error("API unreachable — run `start_api.ps1` first.", icon="🔴")

    st.divider()

    # — Upload section ————————————————————————————————————————————————————————
    st.subheader("📄 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "md", "txt", "html", "htm", "docx", "csv", "json"],
        help="Supported: PDF, Markdown, Text, HTML, Word, CSV, JSON",
    )

    if uploaded_file is not None:
        st.caption(f"Selected: **{uploaded_file.name}**")
        if st.button("🚀 Upload & Index", use_container_width=True, type="primary"):
            with st.spinner(f"Indexing {uploaded_file.name}…"):
                try:
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type or "application/octet-stream",
                        )
                    }
                    r = _post("/api/v1/upload", files=files, timeout=_TIMEOUT_UPLOAD)
                    r.raise_for_status()
                    payload = r.json()
                    new_doc_id = payload["doc_id"]
                    chunks = payload["chunks_indexed"]
                    gcs_uri = payload.get("gcs_uri")

                    # Refresh doc list from server
                    _refresh_docs()

                    # Auto-switch scope to the newly uploaded doc
                    st.session_state.scope_mode = "selected"
                    st.session_state.selected_doc_ids = [new_doc_id]

                    # Clear conversation so history doesn't bleed from old docs
                    _reset_conversation()

                    st.success(f"✅ Indexed **{chunks}** chunks")
                    if gcs_uri:
                        st.caption(f"GCS: `{gcs_uri}`")
                    else:
                        st.caption("GCS upload skipped (no credentials).")
                    st.info(
                        "Conversation reset and scope switched to this document. "
                        "Ask questions below!",
                        icon="🔄",
                    )
                except httpx.HTTPStatusError as e:
                    st.error(f"Server error {e.response.status_code}: {e.response.text}")
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    st.divider()

    # — Document scope selector ———————————————————————————————————————————————
    st.subheader("🗂️ Document Scope")

    col_refresh, col_mode = st.columns([1, 2])
    with col_refresh:
        if st.button("↻", help="Refresh document list from server"):
            _refresh_docs()
            st.rerun()

    docs = st.session_state.indexed_docs
    doc_map = {d["doc_id"]: d for d in docs}  # id → info

    if not docs:
        st.caption("No documents indexed yet. Upload one above.")
        scope_choice = "all"
    else:
        with col_mode:
            scope_choice = st.radio(
                "Query",
                options=["all", "selected"],
                format_func=lambda x: "All documents" if x == "all" else "Selected only",
                index=0 if st.session_state.scope_mode == "all" else 1,
                label_visibility="collapsed",
                key="scope_radio",
            )
        st.session_state.scope_mode = scope_choice

        if scope_choice == "selected":
            # Ensure selected_doc_ids contains only IDs that still exist
            valid_ids = {d["doc_id"] for d in docs}
            current = [i for i in (st.session_state.selected_doc_ids or []) if i in valid_ids]
            st.session_state.selected_doc_ids = current

            st.caption("Check the documents you want to query:")
            new_selection: list[str] = []
            for doc in docs:
                label = f"{doc['filename']} ({doc['chunk_count']} chunks)"
                checked = doc["doc_id"] in (st.session_state.selected_doc_ids or [])
                if st.checkbox(label, value=checked, key=f"doc_{doc['doc_id']}"):
                    new_selection.append(doc["doc_id"])
            st.session_state.selected_doc_ids = new_selection

            if not new_selection:
                st.warning("No documents selected — queries will search all documents.")
        else:
            # Show a summary of all docs
            for doc in docs:
                st.markdown(f"• **{doc['filename']}** — {doc['chunk_count']} chunks")

    # Show active scope badge
    eff = _effective_doc_ids()
    if eff is None:
        st.caption(f"🔍 Querying **all {len(docs)} document(s)**")
    else:
        names = [doc_map[i]["filename"] for i in eff if i in doc_map]
        st.caption(f"🔍 Querying: **{', '.join(names) or 'none selected'}**")

    st.divider()

    # — Session controls ——————————————————————————————————————————————————————
    st.caption(f"Session: `{st.session_state.session_id}`")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        _reset_conversation()
        st.rerun()


# ── main chat area ─────────────────────────────────────────────────────────────

st.title("💬 DocuMind AI")

# Scope label under the title
eff = _effective_doc_ids()
docs = st.session_state.indexed_docs
doc_map = {d["doc_id"]: d for d in docs}
if eff is None:
    if docs:
        st.caption(f"Searching across all {len(docs)} indexed document(s).")
    else:
        st.caption("No documents indexed yet — upload one in the sidebar.")
else:
    names = [doc_map[i]["filename"] for i in eff if i in doc_map]
    st.caption(f"Scope: **{', '.join(names)}**")

# Welcome / empty-state message
if not st.session_state.messages:
    with st.chat_message("assistant"):
        if docs:
            scope_desc = (
                "all indexed documents"
                if eff is None
                else ", ".join(doc_map[i]["filename"] for i in (eff or []) if i in doc_map)
                or "selected documents"
            )
            st.markdown(
                f"Ready! I'll answer from **{scope_desc}**.\n\n"
                "Switch scope or select specific documents in the sidebar."
            )
        else:
            st.markdown(
                "👋 **Welcome to DocuMind AI!**\n\n"
                "Upload a document using the sidebar, then ask me anything about it.\n\n"
                "Supported formats: PDF, Markdown, Text, HTML, Word, CSV, JSON."
            )

# Replay conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask a question about your documentation…"):
    # Append and render user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build query payload
    query_payload: dict = {
        "question": prompt,
        "session_id": st.session_state.session_id,
    }
    eff_ids = _effective_doc_ids()
    if eff_ids:
        query_payload["doc_ids"] = eff_ids

    # Call backend and stream the response
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                r = _post(
                    "/api/v1/query",
                    json=query_payload,
                    timeout=_TIMEOUT_QUERY,
                )
                r.raise_for_status()
                answer = r.json()["answer"]
            except httpx.HTTPStatusError as e:
                answer = f"❌ Server error {e.response.status_code}: {e.response.text}"
            except Exception as e:
                answer = f"❌ Request failed: {e}"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
