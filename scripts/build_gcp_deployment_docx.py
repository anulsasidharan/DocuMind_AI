"""
Generate GCP_deployment_guide.docx (run from repo root).

  pip install python-docx
  python scripts/build_gcp_deployment_docx.py
"""

from __future__ import annotations

import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "GCP_deployment_guide.docx"


def add_title(doc: Document, text: str) -> None:
    h = doc.add_heading(text, 0)
    h.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_h(doc: Document, text: str, level: int = 1) -> None:
    doc.add_heading(text, level=level)


def add_p(doc: Document, text: str) -> None:
    doc.add_paragraph(text)


def add_bullets(doc: Document, items: list[str]) -> None:
    for it in items:
        doc.add_paragraph(it, style="List Bullet")


def add_code(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text.strip("\n"))
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x20, 0x20, 0x20)


def main() -> None:
    try:
        import docx  # noqa: F401
    except ImportError:
        print("Install: python -m pip install python-docx", file=sys.stderr)
        sys.exit(1)

    doc = Document()

    add_title(doc, "DocuMind AI — GCP Deployment Guide")
    add_p(
        doc,
        "Full proof deployment on Google Cloud using Cloud Run, Terraform, Google Cloud Storage (GCS), "
        "Secret Manager, and Artifact Registry. Target stack: FastAPI container (this repository) as the "
        "primary API; GCS for raw documentation objects; optional companion Qdrant deployment for vector search.",
    )
    add_p(doc, "Document version: 1.0 | Generated for DocuMind AI interview / production demo.")

    add_h(doc, "1. What you are deploying", 1)
    add_bullets(
        doc,
        [
            "Container image: FastAPI app (uvicorn api.main:app) built from the project Dockerfile.",
            "Cloud Run service: documind-api (min instances 0–1 per cost/latency trade-off).",
            "GCS bucket: stores source documentation (and optionally processed chunks metadata).",
            "Secrets: OpenAI API key, Qdrant URL/API key, collection name — via Secret Manager, mounted as env vars on Cloud Run.",
            "Terraform: provisions bucket, IAM, Artifact Registry (optional), Cloud Run service, secret bindings.",
            "Not in container by default: Qdrant. Run Qdrant on a second Cloud Run service, GKE, or Qdrant Cloud; point QDRANT_URL at it.",
        ],
    )

    add_h(doc, "2. Prerequisites", 1)
    add_bullets(
        doc,
        [
            "GCP project with billing enabled.",
            "Roles: Project Editor or custom roles covering Cloud Run Admin, Storage Admin, Secret Manager Admin, "
            "Artifact Registry Admin, Service Account User, IAM Security Admin (for bindings).",
            "Tools: gcloud CLI, Terraform >= 1.5, Docker (for local image testing).",
            "Repository clone of DocuMind AI on your workstation.",
        ],
    )

    add_h(doc, "3. Enable required APIs", 1)
    add_p(doc, "Run once per project (replace PROJECT_ID):")
    add_code(
        doc,
        """
gcloud config set project PROJECT_ID

gcloud services enable \\
  run.googleapis.com \\
  storage.googleapis.com \\
  secretmanager.googleapis.com \\
  artifactregistry.googleapis.com \\
  cloudbuild.googleapis.com \\
  iam.googleapis.com
""",
    )

    add_h(doc, "4. High-level architecture", 1)
    add_p(
        doc,
        "Clients call the Cloud Run HTTPS URL for the API. The service reads configuration from environment "
        "variables populated from Secret Manager. Documents live in GCS; indexing (this repo’s scripts/index_docs.py "
        "or a future Cloud Run Job / Vertex pipeline) reads from GCS and writes vectors to Qdrant. The query path "
        "uses OpenAI embeddings + Qdrant retrieval + reranker + GPT-4o.",
    )

    add_h(doc, "5. Terraform layout (recommended)", 1)
    add_p(
        doc,
        "Place the following under terraform/ (split across files as you prefer). Adjust names, regions, and "
        "project_id. This is a complete baseline you can paste and refine.",
    )

    add_h(doc, "5.1 versions.tf", 2)
    add_code(
        doc,
        """
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}
""",
    )

    add_h(doc, "5.2 variables.tf", 2)
    add_code(
        doc,
        """
variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "region" {
  type        = string
  description = "GCP region for Cloud Run and Artifact Registry"
  default     = "europe-west1"
}

variable "documind_api_image" {
  type        = string
  description = "Container image for documind-api (Artifact Registry or gcr.io)"
}

variable "bucket_name" {
  type        = string
  description = "Globally unique GCS bucket name for documentation"
}
""",
    )

    add_h(doc, "5.3 provider.tf", 2)
    add_code(
        doc,
        """
provider "google" {
  project = var.project_id
  region  = var.region
}
""",
    )

    add_h(doc, "5.4 gcs.tf — documentation bucket", 2)
    add_code(
        doc,
        """
resource "google_storage_bucket" "documind_docs" {
  name                        = var.bucket_name
  location                    = var.region
  force_destroy               = false
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 365
    }
  }
}

resource "google_storage_bucket_iam_member" "documind_api_object_viewer" {
  bucket = google_storage_bucket.documind_docs.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.documind_api.email}"
}
""",
    )

    add_h(doc, "5.5 iam.tf — runtime service account", 2)
    add_code(
        doc,
        """
resource "google_service_account" "documind_api" {
  account_id   = "documind-api"
  display_name = "DocuMind API Cloud Run"
}

resource "google_project_iam_member" "documind_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.documind_api.email}"
}

# Optional: if the API ingests from GCS at runtime
resource "google_project_iam_member" "documind_storage_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.documind_api.email}"
}
""",
    )

    add_h(doc, "5.6 secrets.tf — Secret Manager", 2)
    add_p(
        doc,
        "Create secret versions outside Terraform (recommended) so API keys are not stored in state: "
        "echo -n 'sk-...' | gcloud secrets create openai-api-key --data-file=- . "
        "Then reference secret IDs in Cloud Run as shown below.",
    )
    add_code(
        doc,
        """
# Optional: Terraform-managed secrets (avoid putting real values in .tfvars in git)
resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "openai-api-key"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "qdrant_url" {
  secret_id = "qdrant-url"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret" "qdrant_api_key" {
  secret_id = "qdrant-api-key"
  replication {
    auto {}
  }
}
""",
    )

    add_h(doc, "5.7 artifact_registry.tf — Docker repository", 2)
    add_code(
        doc,
        """
resource "google_artifact_registry_repository" "documind" {
  location      = var.region
  repository_id = "documind"
  description   = "DocuMind container images"
  format        = "DOCKER"
}

# After first image push, set documind_api_image to:
# REGION-docker.pkg.dev/PROJECT_ID/documind/documind-api:TAG
""",
    )

    add_h(doc, "5.8 cloud_run.tf — API service", 2)
    add_code(
        doc,
        """
resource "google_cloud_run_v2_service" "documind_api" {
  name     = "documind-api"
  location = var.region

  template {
    service_account = google_service_account.documind_api.email

    containers {
      image = var.documind_api_image

      ports {
        container_port = 8000
      }

      env {
        name = "GCP_PROJECT_ID"
        value_source {
          literal {
            value = var.project_id
          }
        }
      }

      env {
        name = "GCS_BUCKET_DOCS"
        value_source {
          literal {
            value = google_storage_bucket.documind_docs.name
          }
        }
      }

      env {
        name = "ENVIRONMENT"
        value_source {
          literal {
            value = "production"
          }
        }
      }

      env {
        name = "COLLECTION_NAME"
        value_source {
          literal {
            value = "docs-index"
          }
        }
      }

      env {
        name = "OPENAI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.openai_api_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "QDRANT_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.qdrant_url.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "QDRANT_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.qdrant_api_key.secret_id
            version = "latest"
          }
        }
      }
    }

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }

  ingress = "INGRESS_TRAFFIC_ALL"
}

resource "google_cloud_run_v2_service_iam_member" "documind_api_invoker" {
  name     = google_cloud_run_v2_service.documind_api.name
  location = var.region
  role     = "roles/run.invoker"
  member   = "allUsers" # lock down to your org / IAP in production
}
""",
    )

    add_h(doc, "5.9 outputs.tf", 2)
    add_code(
        doc,
        """
output "documind_api_uri" {
  value = google_cloud_run_v2_service.documind_api.uri
}

output "docs_bucket" {
  value = google_storage_bucket.documind_docs.name
}

output "artifact_registry_repo" {
  value = google_artifact_registry_repository.documind.id
}
""",
    )

    add_p(
        doc,
        "Security note: allUsers invoker is convenient for demos; for production use authenticated invokers, "
        "Identity-Aware Proxy, or API Gateway in front of Cloud Run.",
    )

    add_h(doc, "6. Build and push the container image", 1)
    add_p(doc, "From the DocuMind AI repository root (Dockerfile must include all code you need):")
    add_code(
        doc,
        """
gcloud auth configure-docker REGION-docker.pkg.dev

docker build -t REGION-docker.pkg.dev/PROJECT_ID/documind/documind-api:v1 .

docker push REGION-docker.pkg.dev/PROJECT_ID/documind/documind-api:v1
""",
    )
    add_p(
        doc,
        "Alternatively: gcloud builds submit --tag REGION-docker.pkg.dev/PROJECT_ID/documind/documind-api:v1",
    )

    add_h(doc, "7. Create secret values (one-time)", 1)
    add_code(
        doc,
        """
echo -n 'YOUR_OPENAI_KEY' | gcloud secrets versions add openai-api-key --data-file=-

echo -n 'https://your-qdrant-host' | gcloud secrets versions add qdrant-url --data-file=-

echo -n 'YOUR_QDRANT_KEY_OR_EMPTY' | gcloud secrets versions add qdrant-api-key --data-file=-
""",
    )

    add_h(doc, "8. Apply Terraform", 1)
    add_code(
        doc,
        """
cd terraform
terraform init
terraform plan \\
  -var="project_id=PROJECT_ID" \\
  -var="region=europe-west1" \\
  -var="bucket_name=PROJECT_ID-documind-docs" \\
  -var="documind_api_image=REGION-docker.pkg.dev/PROJECT_ID/documind/documind-api:v1"

terraform apply \\
  -var="project_id=PROJECT_ID" \\
  -var="region=europe-west1" \\
  -var="bucket_name=PROJECT_ID-documind-docs" \\
  -var="documind_api_image=REGION-docker.pkg.dev/PROJECT_ID/documind/documind-api:v1"
""",
    )

    add_h(doc, "9. Verify the deployment", 1)
    add_bullets(
        doc,
            [
            "Open Cloud Run URL from terraform output documind_api_uri.",
            "GET /health → JSON status ok.",
            "POST /api/v1/query with {\"question\":\"...\",\"session_id\":\"demo\"} → answer JSON.",
            "Cloud Logging: filter resource.type=cloud_run_revision and textPayload for errors.",
        ],
    )

    add_h(doc, "10. Load documentation into GCS and index", 1)
    add_p(
        doc,
        "Upload markdown or text to the bucket (Console, gsutil, or CI). Example:",
    )
    add_code(
        doc,
        """
gsutil -m cp -r ./local-docs gs://PROJECT_ID-documind-docs/raw/
""",
    )
    add_p(
        doc,
        "Indexing options: (A) Run scripts/index_docs.py from a Cloud Shell VM or developer machine with network "
        "access to Qdrant and OpenAI, reading files downloaded from GCS; (B) add a Cloud Run Job / Workflows step that "
        "runs the indexer container with GCS FUSE or signed URLs; (C) extend the FastAPI /api/v1/index route "
        "(roadmap) to trigger indexing. The current open-source codebase indexes local paths; production typically "
        "adds a small job that streams from GCS.",
    )

    add_h(doc, "11. Qdrant on GCP (required for this app)", 1)
    add_bullets(
        doc,
        [
            "Managed: Qdrant Cloud — simplest; set QDRANT_URL and QDRANT_API_KEY secrets accordingly.",
            "Self-managed: second Cloud Run service with CPU + memory and an attached volume (preview / limited), "
            "or GKE / Compute Engine for persistent disk.",
            "Ensure regional latency: place Qdrant and Cloud Run in the same or adjacent region.",
        ],
    )

    add_h(doc, "12. Optional: Streamlit UI on Cloud Run", 1)
    add_p(
        doc,
        "Build a second image whose CMD runs streamlit run ui/streamlit_app.py --server.port 8080 --server.address 0.0.0.0 "
        "and set Cloud Run container port 8080. Point the UI to the API via a public API URL or internal call pattern. "
        "For interviews, calling the API from Streamlit server-side is acceptable; for production, add auth and CORS policy.",
    )

    add_h(doc, "13. Cost and operations checklist", 1)
    add_bullets(
        doc,
        [
            "Cloud Run: bill on request CPU/memory; set max instances to cap cost.",
            "GCS: standard storage + lifecycle rules for old prefixes.",
            "Secret Manager: per-secret version pricing — rotate keys on schedule.",
            "OpenAI / Qdrant: external bill — monitor usage in application logs.",
            "Enable Cloud Monitoring dashboards for request count, latency, 5xx rate.",
        ],
    )

    add_h(doc, "14. Troubleshooting", 1)
    add_bullets(
        doc,
        [
            "403 on Secret Manager: verify documind-api service account has secretAccessor on each secret.",
            "503 / timeout on first request: cold start + cross-encoder model download; consider min instances = 1 for demo day.",
            "Empty answers: collection empty — run indexer; wrong QDRANT_URL or COLLECTION_NAME.",
            "Image pull errors: verify Artifact Registry permissions for Cloud Run service agent.",
        ],
    )

    add_h(doc, "15. File reference in this repository", 1)
    add_bullets(
        doc,
        [
            "Dockerfile — API production image (port 8000).",
            "api/main.py — FastAPI entrypoint.",
            "terraform/ — replace stub main.tf with the modules above when ready.",
            ".env.example — environment variable contract for local vs Cloud Run.",
        ],
    )

    doc.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
