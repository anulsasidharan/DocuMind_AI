# DocuMind AI

Enterprise-style **documentation question answering** using retrieval-augmented generation (RAG): hybrid-ready retrieval paths, cross-encoder reranking, conversational memory, and a FastAPI backend with an optional Streamlit UI. Designed as a Datatonic interview demo and a base for GCP deployment.

See **CLAUDE.md** for architecture notes and presentation checklist.

## Features

- **RAG pipeline** — OpenAI embeddings, Qdrant vector store, Hugging Face cross-encoder rerank (configurable via `CROSS_ENCODER_MODEL`), GPT-4o answers with citations-focused system prompt  
- **API** — FastAPI: `GET /health`, `POST /api/v1/query`  
- **UI** — Streamlit front end calling the same pipeline  
- **Indexing** — CLI scripts to load `.md`/`.txt` trees into Qdrant  
- **IaC** — Terraform stubs + **GCP_deployment_guide.docx** (Cloud Run, GCS, Secret Manager walkthrough)

## Tech stack

| Layer | Choices |
|--------|---------|
| Orchestration | LangChain (classic retriever + LCEL-style chains) |
| LLM / embeddings | OpenAI (`gpt-4o`, `text-embedding-3-small`) |
| Vector DB | Qdrant |
| Rerank | `CrossEncoderReranker` + Hugging Face model (default `cross-encoder/ms-marco-MiniLM-L-6-v2`) |
| API | FastAPI, Uvicorn |
| UI | Streamlit |

## Prerequisites

- Python **3.11+** recommended (3.x supported with current pins)  
- **Docker** (for local Qdrant via Compose)  
- **OpenAI API key**  

## Quick start (local)

```bash
# From repository root
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env: OPENAI_API_KEY, QDRANT_URL=http://localhost:6333

docker compose up -d
```

Set `PYTHONPATH` to the repo root when running modules (PowerShell: `$env:PYTHONPATH="."`; bash: `export PYTHONPATH=.`).

### Fetch sample GCP-oriented docs (optional)

```bash
python scripts/download_gcp_docs.py
python scripts/index_docs.py data/raw/gcp-docs-samples
```

### Run the API

```bash
uvicorn api.main:app --reload --port 8000
```

Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Run the web UI

```bash
streamlit run ui/streamlit_app.py
```

Opens at [http://localhost:8501](http://localhost:8501) by default.

### Legacy one-liner script

```bash
python documentation-qa.py
```

## Configuration

Environment variables are documented in `.env.example`. Important keys:

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | OpenAI authentication |
| `QDRANT_URL` | Qdrant HTTP URL |
| `QDRANT_API_KEY` | Optional, if Qdrant is secured |
| `COLLECTION_NAME` | Qdrant collection (default `docs-index`) |
| `CROSS_ENCODER_MODEL` | Hugging Face cross-encoder id for reranking |

Runtime settings load through `src/config.py` (Pydantic Settings).

## Tests

```bash
pytest
```

`tests/test_rag_pipeline.py` includes a skipped integration case; enable it after keys, Qdrant, and indexing are ready.

## Project layout

```
documind-ai/
├── api/              # FastAPI app (main, routes, models)
├── src/              # config, embeddings, llm, retriever, reranker, rag_pipeline
├── pipelines/        # chunker, loader, embedder stubs; Vertex-style expansion later
├── ui/               # Streamlit
├── scripts/          # index_docs, download_gcp_docs, GCP docx generator
├── tests/
├── terraform/        # stubs; merge with GCP guide when deploying
├── data/raw/         # clone / upload docs here for indexing
├── docker-compose.yml
├── Dockerfile
├── GCP_deployment_guide.docx
└── README.md
```

## GCP deployment

Use **`GCP_deployment_guide.docx`** at the repo root for a step-by-step guide: Artifact Registry image build, Terraform for **Cloud Run**, **GCS**, IAM, Secret Manager, and verification. Regenerate or edit the Word file via:

```bash
pip install python-docx
python scripts/build_gcp_deployment_docx.py
```

## License

Specify your license here (for example MIT) if you publish the repo.
