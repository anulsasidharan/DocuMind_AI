"""Streamlit UI (Phase 4 — minimal shell for local testing)."""

import os
import sys
from pathlib import Path

# Ensure project root on path when run as `streamlit run ui/streamlit_app.py`
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st

st.set_page_config(page_title="DocuMind AI", layout="wide")
st.title("DocuMind AI")
st.caption("Documentation Q&A — wire to API or call `src.rag_pipeline.query` in later phase.")

question = st.text_input("Question", placeholder="Ask about GCP documentation…")
session_id = st.text_input("Session ID", value="streamlit-default")

if st.button("Ask") and question:
    if not os.environ.get("OPENAI_API_KEY"):
        st.warning("Set OPENAI_API_KEY and QDRANT_URL in your environment or `.env`.")
    else:
        from src.rag_pipeline import query as rag_query

        with st.spinner("Retrieving and generating…"):
            answer = rag_query(question, session_id=session_id)
        st.markdown(answer)
