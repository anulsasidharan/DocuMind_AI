# DocuMind AI

Enterprise-style **documentation question answering** using retrieval-augmented generation (RAG): hybrid-ready retrieval paths, cross-encoder reranking, conversational memory, and a FastAPI backend with an optional Streamlit UI. Designed as a Datatonic interview demo and a base for GCP deployment.

See **CLAUDE.md** for architecture notes and presentation checklist.

## Features

- **RAG pipeline** — OpenAI embeddings, Qdrant vector store, Hugging Face cross-encoder rerank (configurable via `CROSS_ENCODER_MODEL`), GPT-4o answers with citations-focused system prompt  
- **API** — FastAPI: `GET /health`, `POST /api/v1/upload`, `POST /api/v1/query`, `POST /api/v1/upload-query`  
- **Chat UI** — Streamlit with sidebar document upload and a persistent chat interface (conversation history per session)  
- **Multi-format ingestion** — PDF, Markdown, TXT, HTML, DOCX, CSV, JSON; GCS upload optional (gracefully skipped when credentials are absent)  
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

### Run with Docker (API + WebUI + Qdrant)

From the repo root, with a valid **`.env`** (at least `OPENAI_API_KEY`; `QDRANT_URL` can stay `http://localhost:6333` for local non-Docker—the Compose file overrides it to **`http://qdrant:6333`** inside the network):

```bash
docker compose build
docker compose up -d
```

- **API:** [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs) (host port **8001** if 8000 is busy on your machine).
- **Web UI (Streamlit):** [http://127.0.0.1:8501](http://127.0.0.1:8501)
- **Qdrant dashboard (host):** [http://127.0.0.1:6335/dashboard](http://127.0.0.1:6335/dashboard) when using the default `docker-compose.yml` port mapping (**6335** avoids clashes with another Qdrant on 6333).

The Streamlit UI includes:
- **Ask Existing Index** (uses `POST /api/v1/query`)
- **Upload -> GCS -> Index -> Ask** (uses `POST /api/v1/upload-query`)

For upload-to-GCS flow, set these in `.env`:
- `GCS_BUCKET_DOCS=<your-bucket>`
- `GCP_PROJECT_ID=<your-project>`
- `GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-sa.json` and place your key at `./gcp/gcp-sa.json` (for local Docker runs)

Index docs **inside** the API container (example):

```bash
docker compose exec api python scripts/index_docs.py /app/data/raw/gcp-docs-samples
```

`./data` on your machine is mounted read-only at `/app/data` in the container.

```bash
docker compose logs -f api
docker compose down
```

### Fetch sample GCP-oriented docs (optional)

```bash
python scripts/download_gcp_docs.py
python scripts/index_docs.py data/raw/gcp-docs-samples
```

### Run the API (PowerShell — recommended, handles env vars correctly)

```powershell
.\start_api.ps1          # starts on port 8001 (avoids common port 8000 conflicts)
.\start_api.ps1 -Port 8000   # or choose your own port
```

Interactive docs: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)

Or manually (ensure `.env` is in your working directory):

```bash
uvicorn api.main:app --reload --port 8001
```

### Run the web UI

```powershell
.\start_ui.ps1                           # connects to API on port 8001
.\start_ui.ps1 -ApiUrl http://127.0.0.1:8000   # custom API URL
```

Or manually:

```bash
DOCUMIND_API_URL=http://127.0.0.1:8001 streamlit run ui/streamlit_app.py
```

Opens at [http://localhost:8501](http://localhost:8501).  
Upload a document in the **sidebar**, then ask questions in the **chat interface**.

### Workflow

1. Start the API server (`start_api.ps1`)  
2. Start the Streamlit UI (`start_ui.ps1` in a second terminal)  
3. Open [http://localhost:8501](http://localhost:8501)  
4. Upload a document (PDF/MD/TXT/HTML/DOCX/CSV/JSON) in the sidebar  
5. Wait for "Indexed N chunks" confirmation  
6. Ask questions in the chat — answers include citations from your documents

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
