FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only PyTorch first (default pip wheels pull huge CUDA stacks on Linux).
RUN grep -vE '^torch' requirements.txt > /tmp/requirements-no-torch.txt \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r /tmp/requirements-no-torch.txt

COPY src/ ./src/
COPY api/ ./api/
COPY pipelines/ ./pipelines/
COPY scripts/ ./scripts/
COPY ui/ ./ui/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
