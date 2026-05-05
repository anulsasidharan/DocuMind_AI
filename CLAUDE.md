# DocuMind AI - Production Documentation Q&A RAG System

> **Intelligent Documentation Retrieval with Hybrid Search and Reranking on Google Cloud Platform**

**Project Type:** Machine Learning Engineering - RAG Pipeline  
**Cloud Provider:** Google Cloud Platform (GCP)  
**Target:** Datatonic ML Engineer Interview Demo  
**Timeline:** 1-day rapid development  
**Developer:** Anu Sasidharan | OrionVexa

---

## 🎯 Project Overview

DocuMind AI is an enterprise-grade Retrieval-Augmented Generation (RAG) system designed for intelligent documentation querying. The system combines hybrid search (dense + sparse retrieval), cross-encoder reranking, and conversation memory to deliver accurate, context-aware answers from technical documentation.

### Key Value Proposition
- **High Accuracy:** Hybrid search + reranking achieves superior retrieval precision
- **Production-Ready:** Fully containerized, scalable GCP deployment
- **Cost-Optimized:** Efficient resource usage with autoscaling
- **Enterprise Features:** Conversation history, citation tracking, monitoring

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                   (Streamlit / FastAPI + React)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API GATEWAY (Cloud Run)                      │
│                        FastAPI Backend                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Embeddings │ │   Retrieval  │ │     LLM      │
│   (OpenAI    │ │  (Qdrant +   │ │  (GPT-4o)    │
│   text-emb-  │ │  Reranker)   │ │              │
│   3-small)   │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │    Vector Database (Qdrant)   │
         │    (Cloud Run or GKE)         │
         └───────────────────────────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │   Document Storage (GCS)      │
         │   - Source Docs               │
         │   - Processed Chunks          │
         └───────────────────────────────┘
```

### Component Stack

| Component | Technology | GCP Service | Purpose |
|-----------|-----------|-------------|---------|
| **API Backend** | FastAPI | Cloud Run | Serverless API endpoint |
| **Embeddings** | OpenAI text-embedding-3-small | External API | Document vectorization |
| **LLM** | GPT-4o | OpenAI API | Answer generation |
| **Vector DB** | Qdrant | Cloud Run / GKE | Hybrid search + filtering |
| **Reranker** | Cohere Rerank v3 | In-process | Result reranking |
| **Storage** | GCS | Cloud Storage | Document repository |
| **Orchestration** | Vertex AI Pipelines | Vertex AI | Indexing pipeline |
| **Monitoring** | Cloud Logging + Prometheus | Cloud Operations | Observability |
| **IaC** | Terraform | - | Infrastructure automation |

---

## 🔧 Technical Implementation

### 1. RAG Pipeline Components

#### A. Document Ingestion
```python
# Workflow:
# 1. Upload docs to GCS bucket
# 2. Trigger Cloud Function / Vertex AI Pipeline
# 3. Load → Chunk → Embed → Store

CHUNK_SIZE = 512 tokens
CHUNK_OVERLAP = 50 tokens
SEPARATORS = ["\n\n", "\n", ". ", " ", ""]
```

**Supported Formats:**
- Markdown (.md)
- HTML documentation
- PDF technical docs
- ReStructuredText (.rst)
- Plain text

#### B. Hybrid Retrieval Strategy

**Dense Retrieval (Vector Search):**
- Model: `text-embedding-3-small` (1536 dimensions)
- Distance: Cosine similarity
- Initial K: 8 documents

**Sparse Retrieval (BM25):**
- Keyword-based lexical search
- Ensemble weight: 40% BM25, 60% Dense

**Reranking:**
- Model: `cohere-rerank-v3` (cross-encoder)
- Top-N after reranking: 5 documents

#### C. Prompt Engineering
```python
SYSTEM_PROMPT = """
You are a technical documentation assistant for {DOMAIN}.

CONTEXT:
{retrieved_context}

INSTRUCTIONS:
1. Answer based strictly on provided context
2. Include code examples when relevant
3. Cite source sections (e.g., "According to Section 3.2...")
4. If information is missing, state: "This information is not in the documentation."
5. Format using Markdown with proper code blocks

ANSWER:
"""
```

### 2. GCP Deployment Architecture

#### Infrastructure Components

**Cloud Run Services:**
```
documind-api:
  - CPU: 2 vCPU
  - Memory: 4 GB
  - Min instances: 0
  - Max instances: 10
  - Autoscaling: CPU 70%

qdrant-vectordb:
  - CPU: 2 vCPU
  - Memory: 8 GB
  - Min instances: 1 (always on)
  - Persistent disk: 50 GB SSD
```

**Cloud Storage Buckets:**
```
documind-source-docs/
  ├── raw/              # Original uploaded docs
  ├── processed/        # Chunked + metadata
  └── embeddings/       # Embedding cache (optional)

documind-model-artifacts/
  └── reranker/         # Cached reranker model
```

**Vertex AI Pipeline:**
```
indexing-pipeline:
  Trigger: GCS file upload (Cloud Function)
  Steps:
    1. Document loading
    2. Text chunking
    3. Embedding generation (batched)
    4. Qdrant insertion
    5. Metadata indexing
  Schedule: On-demand + weekly full reindex
```

### 3. API Endpoints

**FastAPI Routes:**
```python
POST /api/v1/query
  Body: {"question": str, "session_id": str}
  Response: {"answer": str, "sources": [...], "confidence": float}

POST /api/v1/index
  Body: {"file_urls": [str], "collection": str}
  Response: {"job_id": str, "status": str}

GET /api/v1/status/{job_id}
  Response: {"status": str, "chunks_processed": int}

GET /api/v1/collections
  Response: {"collections": [...]}

DELETE /api/v1/collections/{name}
  Response: {"deleted": bool}
```

---

## 📊 Data Strategy

### Open-Source Documentation Datasets

**Option 1: GCP Documentation (Primary)**
```bash
# Scrape GCP official docs
git clone https://github.com/GoogleCloudPlatform/python-docs-samples
# Extract markdown files from docs/ folders
```

**Option 2: Python Documentation**
```bash
# Download Python 3.12 docs
wget https://docs.python.org/3.12/archives/python-3.12-docs-html.zip
# Parse HTML to markdown
```

**Option 3: Kubernetes Documentation**
```bash
git clone https://github.com/kubernetes/website
cd website/content/en/docs/
# Process markdown files
```

**Option 4: Hugging Face Datasets**
```python
from datasets import load_dataset
# Use pre-processed documentation datasets
dataset = load_dataset("squad")  # For QA pairs
dataset = load_dataset("ms_marco")  # For retrieval benchmarks
```

### Data Preprocessing Pipeline

```python
# Vertex AI Pipeline Steps

@component
def load_documents(gcs_path: str) -> List[Document]:
    """Load docs from GCS bucket"""
    # Implementation

@component
def chunk_documents(docs: List[Document]) -> List[Document]:
    """Split into chunks with RecursiveCharacterTextSplitter"""
    # Implementation

@component
def generate_embeddings(chunks: List[Document]) -> List[np.ndarray]:
    """Batch embed with OpenAI API"""
    # Implementation with retry logic

@component
def upsert_to_qdrant(chunks: List[Document], embeddings: List):
    """Bulk insert to Qdrant with metadata"""
    # Implementation

@pipeline(name="documind-indexing")
def indexing_pipeline(source_bucket: str):
    docs = load_documents(source_bucket)
    chunks = chunk_documents(docs)
    embeddings = generate_embeddings(chunks)
    upsert_to_qdrant(chunks, embeddings)
```

---

## 🚀 Implementation Roadmap (1-Day Sprint)

### Phase 1: Core RAG Pipeline (3 hours)
- [x] ✅ Base code structure (provided)
- [ ] 🔧 Set up local development environment
- [ ] 🔧 Implement document loader for markdown
- [ ] 🔧 Test chunking strategy locally
- [ ] 🔧 Set up Qdrant locally (Docker)
- [ ] 🔧 Implement basic query flow

### Phase 2: GCP Integration (2 hours)
- [ ] 🔧 Create GCP project
- [ ] 🔧 Set up Cloud Storage buckets
- [ ] 🔧 Deploy Qdrant to Cloud Run
- [ ] 🔧 Create Vertex AI Pipeline for indexing
- [ ] 🔧 Set up Secret Manager for API keys

### Phase 3: API Development (2 hours)
- [ ] 🔧 Build FastAPI backend
- [ ] 🔧 Implement `/query` endpoint
- [ ] 🔧 Add conversation history
- [ ] 🔧 Deploy to Cloud Run
- [ ] 🔧 Test end-to-end flow

### Phase 4: Frontend & Demo (1.5 hours)
- [ ] 🔧 Create Streamlit UI
- [ ] 🔧 Add example queries
- [ ] 🔧 Implement source citation display
- [ ] 🔧 Deploy Streamlit to Cloud Run

### Phase 5: Monitoring & Polish (1.5 hours)
- [ ] 🔧 Add Cloud Logging
- [ ] 🔧 Set up basic metrics (latency, tokens)
- [ ] 🔧 Create Terraform scripts
- [ ] 🔧 Write README and architecture docs
- [ ] 🔧 Record demo video (optional)

---

## 📁 Project Structure

```
documind-ai/
├── README.md
├── CLAUDE.md                    # This file
├── requirements.txt
├── Dockerfile
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── config.py                # Configuration management
│   ├── rag_pipeline.py          # Core RAG logic (refactored)
│   ├── embeddings.py            # Embedding utilities
│   ├── retriever.py             # Retrieval strategies
│   ├── reranker.py              # Reranking logic
│   └── llm.py                   # LLM interface
│
├── api/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app
│   ├── routes.py                # API endpoints
│   └── models.py                # Pydantic schemas
│
├── pipelines/
│   ├── indexing_pipeline.py     # Vertex AI Pipeline
│   └── components/
│       ├── loader.py
│       ├── chunker.py
│       └── embedder.py
│
├── ui/
│   └── streamlit_app.py         # Streamlit frontend
│
├── data/
│   ├── raw/                     # Sample docs for testing
│   └── processed/               # Chunked outputs
│
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── cloud-run.tf
│   ├── storage.tf
│   └── iam.tf
│
├── tests/
│   ├── test_rag_pipeline.py
│   ├── test_api.py
│   └── test_retrieval.py
│
├── scripts/
│   ├── setup_gcp.sh             # GCP project setup
│   ├── deploy.sh                # Deployment script
│   ├── index_docs.py            # CLI for indexing
│   └── benchmark.py             # Retrieval benchmarks
│
└── docs/
    ├── ARCHITECTURE.md
    ├── API_REFERENCE.md
    ├── DEPLOYMENT.md
    └── PRESENTATION.md          # Interview presentation notes
```

---

## 🔐 Security & Configuration

### Environment Variables
```bash
# .env
OPENAI_API_KEY=sk-...
QDRANT_URL=https://qdrant-xxx.run.app
QDRANT_API_KEY=xxx
GCP_PROJECT_ID=documind-ai-prod
GCS_BUCKET_DOCS=documind-source-docs
GCS_BUCKET_ARTIFACTS=documind-model-artifacts
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### GCP Secret Manager Setup
```bash
# Store sensitive credentials
gcloud secrets create openai-api-key --data-file=./openai_key.txt
gcloud secrets create qdrant-api-key --data-file=./qdrant_key.txt

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:documind-api@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

---

## 📈 Monitoring & Observability

### Key Metrics to Track

**Performance Metrics:**
- Query latency (p50, p95, p99)
- Retrieval time
- Reranking time
- LLM generation time
- Total end-to-end latency

**Quality Metrics:**
- Retrieval precision@5
- Answer relevance score
- Citation accuracy
- User feedback (thumbs up/down)

**Cost Metrics:**
- OpenAI API costs (embeddings + completions)
- Qdrant compute costs
- Cloud Run instance hours
- Total cost per query

### Cloud Logging Setup
```python
import google.cloud.logging

# Initialize Cloud Logging
client = google.cloud.logging.Client()
client.setup_logging()

# Log structured data
logger.info("Query processed", extra={
    "query": question,
    "latency_ms": latency,
    "chunks_retrieved": len(chunks),
    "tokens_used": tokens,
    "cost_usd": cost
})
```

---

## 💰 Cost Estimation

### Monthly Cost Breakdown (Assuming 10K queries/month)

| Component | Unit Cost | Monthly Usage | Total |
|-----------|-----------|---------------|-------|
| **OpenAI Embeddings** | $0.02 / 1M tokens | ~500K tokens | $0.01 |
| **OpenAI GPT-4o** | $2.50 / 1M tokens (in) | ~10M tokens | $25.00 |
| **OpenAI GPT-4o** | $10.00 / 1M tokens (out) | ~2M tokens | $20.00 |
| **Cohere Rerank** | $1.00 / 1K searches | 10K searches | $10.00 |
| **Cloud Run (API)** | ~$0.10 / vCPU-hour | 20 hours | $2.00 |
| **Cloud Run (Qdrant)** | ~$0.20 / GB-month | 8 GB | $1.60 |
| **Cloud Storage** | $0.02 / GB | 10 GB | $0.20 |
| **Vertex AI Pipelines** | Minimal (on-demand) | - | $0.50 |
| **Networking** | Negligible | - | $0.50 |
| **TOTAL** | | | **~$60/month** |

**Cost Optimization Strategies:**
- Cache frequent queries (Redis)
- Use smaller embedding models for non-critical queries
- Implement rate limiting
- Use GPT-4o-mini for simpler questions

---

## 🎤 Presentation Strategy (10-15 min)

### Slide Structure (8 slides)

**Slide 1: Title & Problem Statement**
- DocuMind AI: Intelligent Documentation Q&A
- Problem: Developers waste 20% of time searching docs
- Solution: Production-grade RAG with hybrid search

**Slide 2: Architecture Overview**
- High-level diagram
- Highlight GCP-native components
- Emphasize scalability and cost-efficiency

**Slide 3: Technical Deep Dive - Retrieval**
- Hybrid search: Dense (vector) + Sparse (BM25)
- Cross-encoder reranking
- Evaluation metrics (precision@5, recall@10)

**Slide 4: MLOps Pipeline**
- Vertex AI Pipelines for document indexing
- Automated reindexing workflow
- CI/CD with Cloud Build

**Slide 5: Live Demo**
- Show Streamlit UI
- Query: "How do I deploy a model to Vertex AI?"
- Highlight: source citation, response quality

**Slide 6: Monitoring & Production Readiness**
- Cloud Logging dashboard
- Latency metrics
- Cost tracking

**Slide 7: Challenges & Learnings**
- Challenge 1: Reranker latency → Solution: Async processing
- Challenge 2: Chunking strategy → Solution: Overlapping windows
- Challenge 3: Cost control → Solution: Caching + rate limiting

**Slide 8: Future Enhancements**
- Multi-modal support (code diagrams, API schemas)
- Fine-tuned reranker for domain-specific docs
- Graph RAG for relationship queries
- Integration with Google Workspace

### Q&A Preparation Topics

**Expect questions on:**
1. **Why hybrid search over pure vector search?**
   - Answer: Combines semantic understanding with keyword precision
   - Example: "Kubernetes deployment" benefits from both

2. **Why Cohere rerank vs. training custom reranker?**
   - Answer: Time-to-value, state-of-the-art performance out-of-box
   - Custom reranker requires labeled data and training infra

3. **How would you handle multi-lingual documentation?**
   - Answer: Multilingual embeddings (e.g., `multilingual-e5-large`)
   - Language detection + routing to language-specific models

4. **Scaling to millions of documents?**
   - Answer: Qdrant clustering, sharding by collection
   - Approximate nearest neighbor (ANN) with HNSW index

5. **How do you evaluate RAG quality?**
   - Answer: Retrieval metrics (precision, recall, MRR)
   - End-to-end: RAGAS framework (faithfulness, relevance)

6. **Production failure modes?**
   - Answer: OpenAI API rate limits, Qdrant OOM, stale embeddings
   - Mitigations: Retry logic, circuit breakers, monitoring

---

## 🧪 Testing & Validation

### Unit Tests
```python
# tests/test_retrieval.py
def test_chunking_preserves_context():
    doc = "Long document..."
    chunks = text_splitter.split_text(doc)
    assert all(len(chunk) <= CHUNK_SIZE for chunk in chunks)
    assert chunks[0][-CHUNK_OVERLAP:] in chunks[1]  # Overlap check

def test_retrieval_returns_top_k():
    query = "How to deploy on GCP?"
    results = retriever.get_relevant_documents(query)
    assert len(results) == TOP_K
```

### Integration Tests
```python
# tests/test_api.py
def test_query_endpoint():
    response = client.post("/api/v1/query", json={
        "question": "What is Vertex AI?",
        "session_id": "test-123"
    })
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "sources" in response.json()
```

### Retrieval Benchmarks
```python
# scripts/benchmark.py
# Use MS MARCO or BEIR datasets for retrieval evaluation
from beir import util
from beir.retrieval.evaluation import EvaluateRetrieval

# Compute Recall@k, NDCG@k, MAP
results = EvaluateRetrieval.evaluate(qrels, results, k_values=[5, 10, 20])
```

---

## 🛠️ Development Setup

### Local Development
```bash
# 1. Clone repo
git clone https://github.com/anulsasidharan/documind-ai.git
cd documind-ai

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Run Qdrant locally
docker run -p 6333:6333 qdrant/qdrant

# 6. Index sample documents
python scripts/index_docs.py --source data/raw/gcp-docs/

# 7. Start API server
uvicorn api.main:app --reload --port 8000

# 8. Start Streamlit UI (separate terminal)
streamlit run ui/streamlit_app.py
```

### GCP Deployment
```bash
# 1. Authenticate
gcloud auth login
gcloud config set project documind-ai-prod

# 2. Deploy infrastructure
cd terraform
terraform init
terraform plan
terraform apply

# 3. Deploy services
./scripts/deploy.sh

# 4. Run indexing pipeline
python pipelines/indexing_pipeline.py \
  --source gs://documind-source-docs/raw/ \
  --collection gcp-docs
```

---

## 📚 Key Dependencies

```txt
# requirements.txt
langchain==0.1.20
langchain-openai==0.1.7
langchain-qdrant==0.1.1
langchain-community==0.0.38

qdrant-client==1.8.0
openai==1.14.0

fastapi==0.110.0
uvicorn[standard]==0.27.1
pydantic==2.6.3

streamlit==1.32.0

google-cloud-storage==2.14.0
google-cloud-logging==3.9.0
google-cloud-secret-manager==2.18.2

sentence-transformers==2.5.1  # For local testing
cohere==4.57  # For reranking

python-dotenv==1.0.1
pytest==8.0.2
pytest-asyncio==0.23.5

# For Vertex AI Pipelines
kfp==2.7.0
google-cloud-aiplatform==1.43.0
```

---

## 🎯 Success Metrics for Interview

**What Makes This Demo Strong:**
1. ✅ **Production-ready**: Not just a Jupyter notebook, full deployment
2. ✅ **GCP-native**: Uses Vertex AI, Cloud Run, GCS
3. ✅ **ML Engineering depth**: Hybrid search, reranking, evaluation
4. ✅ **Data-focused**: Real documentation corpus, not toy dataset
5. ✅ **Scalable**: Terraform IaC, containerized services
6. ✅ **Monitored**: Logging, metrics, cost tracking
7. ✅ **Tested**: Unit tests, integration tests, benchmarks

**Differentiation from Basic RAG Demos:**
- Most demos: Single Jupyter notebook, OpenAI + Pinecone, no deployment
- This demo: Full stack, GCP-native, production monitoring, MLOps pipeline

---

## 🔗 Additional Resources

**GCP Documentation:**
- [Vertex AI Pipelines](https://cloud.google.com/vertex-ai/docs/pipelines)
- [Cloud Run Best Practices](https://cloud.google.com/run/docs/best-practices)
- [Secret Manager](https://cloud.google.com/secret-manager/docs)

**RAG Resources:**
- [LangChain RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [RAGAS Evaluation Framework](https://docs.ragas.io/)

**Datasets:**
- [MS MARCO](https://microsoft.github.io/msmarco/)
- [BEIR Benchmark](https://github.com/beir-cellar/beir)
- [GCP Samples Repo](https://github.com/GoogleCloudPlatform/python-docs-samples)

---

## 📝 Interview Talking Points

### Opening (1 min)
"Hi, I'm Anu. Today I'm presenting DocuMind AI, a production-ready documentation Q&A system I built on Google Cloud Platform. This demonstrates my approach to ML Engineering: not just model performance, but scalability, cost-efficiency, and operational excellence."

### Demo Script (3 min)
1. Show architecture diagram
2. Live query: "How do I configure autoscaling in GKE?"
3. Highlight: retrieved sources, citations, response quality
4. Show Cloud Logging dashboard with latency metrics

### Technical Deep Dive (5 min)
- Walk through hybrid retrieval strategy
- Explain reranking motivation and impact
- Show Vertex AI pipeline for indexing
- Discuss cost optimization decisions

### Challenges & Learnings (2 min)
- Initial chunking strategy was too coarse → overlapping windows
- Reranker latency was bottleneck → async processing
- Cost spiraled in testing → added caching and rate limiting

### Closing (1 min)
"This project showcases my ability to take ML research concepts—hybrid retrieval, cross-encoder reranking—and operationalize them on GCP with production monitoring and cost controls. I'm excited about applying these skills at Datatonic."

---

## ✅ Pre-Interview Checklist

**24 Hours Before:**
- [ ] Full deployment tested on GCP
- [ ] Sample queries prepared and tested
- [ ] Presentation slides finalized
- [ ] Architecture diagram exported as PNG
- [ ] Demo video recorded (backup if live demo fails)
- [ ] Cost dashboard screenshot captured
- [ ] GitHub repo cleaned up and README polished

**Day Of:**
- [ ] Test internet connection for live demo
- [ ] Have backup slides with screenshots
- [ ] Qdrant service confirmed running
- [ ] API endpoint responding (curl test)
- [ ] Presentation rehearsed (10 min timing)

---

## 🏆 Why This Project Stands Out

**For Datatonic Specifically:**
1. **GCP-Native**: Uses Vertex AI, Cloud Run, not AWS/Azure
2. **Data-Focused**: Documentation is structured data at scale
3. **Production-Grade**: Not a notebook, actual deployment
4. **Cost-Aware**: Shows business acumen beyond ML
5. **MLOps Mindset**: Pipeline automation, monitoring, testing

**Compared to Example Ideas in Interview Doc:**
- ✅ More ambitious than "basic RAG system"
- ✅ Shows production thinking beyond "Vertex AI pipeline to train sklearn"
- ✅ Demonstrates full ML lifecycle, not just training
- ✅ Has actual user-facing interface, not just backend

---

## 🚀 Post-Interview Extensions (If Asked)

**"What would you add with more time?"**
1. Fine-tuned reranker on domain-specific data
2. Multi-modal support (extract info from diagrams)
3. Graph RAG for relationship queries ("How do X and Y interact?")
4. A/B testing framework for retrieval strategies
5. User feedback loop for continuous improvement

**"How would you scale this to 1M queries/day?"**
1. Qdrant clustering with sharding
2. Query result caching (Redis)
3. Rate limiting and quota management
4. Async processing with Cloud Tasks
5. CDN for static UI assets

---

## 📧 Contact & Links

**Developer:** Anu Sasidharan  
**Email:** anu.sasidharan@orionvexa.ca  
**Portfolio:** https://anulsasidharan.github.io  
**GitHub:** https://github.com/anulsasidharan/documind-ai  
**LinkedIn:** https://linkedin.com/in/anulsasidharan  

**Project Repository:** `documind-ai` (to be created)  
**Demo URL:** https://documind-ui-xxx.run.app (to be deployed)  
**Presentation Slides:** [Google Slides Link] (to be created)

---

**Last Updated:** May 5, 2025  
**Status:** 🚧 In Development - Interview Demo Build  
**License:** MIT (for portfolio purposes)

---

## 🎓 Learning Outcomes

By building this project, you demonstrate mastery of:
- ✅ RAG architecture design and implementation
- ✅ Hybrid retrieval strategies (dense + sparse)
- ✅ Cross-encoder reranking for precision improvement
- ✅ GCP service orchestration (Cloud Run, Vertex AI, GCS)
- ✅ MLOps pipeline development
- ✅ Production monitoring and cost optimization
- ✅ API design with FastAPI
- ✅ Infrastructure as Code (Terraform)
- ✅ Containerization and deployment
- ✅ ML system evaluation and benchmarking

---

**Remember:** The goal is to show your ML Engineering skills, problem-solving approach, and passion for building production ML systems. Focus on demonstrating technical depth in the Q&A session—they will go low-level on design decisions and code!

**Good luck with your interview! 🚀**
