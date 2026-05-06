"""Streamlit chat UI for DocuMind AI."""

from __future__ import annotations

import os
import uuid

import httpx
import streamlit as st

API_URL = os.environ.get("DOCUMIND_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="DocuMind AI", page_icon="📚", layout="wide")

# ── Session state ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files: list[dict] = []

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📚 DocuMind AI")
    st.caption("Intelligent Documentation Q&A")
    st.divider()

    # Health check indicator
    try:
        health_r = httpx.get(f"{API_URL}/health", timeout=3)
        if health_r.status_code == 200:
            st.success("API connected", icon="✅")
        else:
            st.warning("API returned non-200", icon="⚠️")
    except Exception:
        st.error("API unreachable — start the FastAPI server first.", icon="🔴")

    st.divider()
    st.subheader("📄 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "md", "txt", "html", "htm", "docx", "csv", "json"],
        help="Supported formats: PDF, Markdown, Text, HTML, Word, CSV, JSON",
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
                    r = httpx.post(f"{API_URL}/api/v1/upload", files=files, timeout=300)
                    r.raise_for_status()
                    payload = r.json()
                    chunks = payload["chunks_indexed"]
                    gcs_uri = payload.get("gcs_uri")
                    st.session_state.indexed_files.append(
                        {"name": uploaded_file.name, "chunks": chunks, "gcs_uri": gcs_uri}
                    )
                    st.success(f"Indexed **{chunks}** chunks from {uploaded_file.name}")
                    if gcs_uri:
                        st.caption(f"Stored at: `{gcs_uri}`")
                    else:
                        st.caption("GCS upload skipped (no credentials configured).")
                except httpx.HTTPStatusError as e:
                    st.error(f"Server error {e.response.status_code}: {e.response.text}")
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    # Indexed documents list
    if st.session_state.indexed_files:
        st.divider()
        st.subheader("📑 Indexed Documents")
        for doc in st.session_state.indexed_files:
            st.markdown(f"• **{doc['name']}** — {doc['chunks']} chunks")

    st.divider()
    st.caption(f"Session ID: `{st.session_state.session_id}`")
    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.session_state.messages = []
        st.rerun()

# ── Main chat area ────────────────────────────────────────────────────────────
st.title("💬 DocuMind AI")
st.caption("Ask questions about your uploaded documentation.")

# Welcome message when no conversation yet
if not st.session_state.messages:
    with st.chat_message("assistant"):
        if st.session_state.indexed_files:
            names = ", ".join(d["name"] for d in st.session_state.indexed_files)
            st.markdown(
                f"Documents indexed: **{names}**. What would you like to know?"
            )
        else:
            st.markdown(
                "👋 **Welcome to DocuMind AI!**\n\n"
                "Upload a document using the sidebar on the left, then ask me anything about it.\n\n"
                "Supported formats: PDF, Markdown, Text, HTML, Word, CSV, JSON."
            )

# Replay conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input — always shown
if prompt := st.chat_input("Ask a question about your documentation…"):
    # Append and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Query the backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                r = httpx.post(
                    f"{API_URL}/api/v1/query",
                    json={"question": prompt, "session_id": st.session_state.session_id},
                    timeout=120,
                )
                r.raise_for_status()
                answer = r.json()["answer"]
            except httpx.HTTPStatusError as e:
                answer = f"❌ Server error {e.response.status_code}: {e.response.text}"
            except Exception as e:
                answer = f"❌ Request failed: {e}"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
