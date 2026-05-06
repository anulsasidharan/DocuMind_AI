# ── Required variables ────────────────────────────────────────────────────────

variable "project_id" {
  type        = string
  description = "GCP project ID  (gcloud config get-value project)"
}

variable "gcs_bucket_docs" {
  type        = string
  description = "Globally-unique GCS bucket name for uploaded source documents (suggestion: PROJECT_ID-documind-docs)"
}

variable "api_image" {
  type        = string
  description = "Full Artifact Registry path for the API image — set after first docker push"
  # e.g.  us-central1-docker.pkg.dev/PROJECT_ID/documind/api:v1
}

variable "webui_image" {
  type        = string
  description = "Full Artifact Registry path for the WebUI image (same Docker image as api_image, different CMD override in Cloud Run)"
  # e.g.  us-central1-docker.pkg.dev/PROJECT_ID/documind/api:v1
}

# ── Optional variables (defaults provided) ───────────────────────────────────

variable "region" {
  type        = string
  description = "Primary GCP region for Cloud Run, Artifact Registry, and GCS"
  default     = "us-central1"
}

variable "collection_name" {
  type        = string
  description = "Qdrant collection name used by the application"
  default     = "documindai"
}

variable "environment" {
  type        = string
  description = "Deployment environment label (used for resource labels)"
  default     = "production"
}

variable "api_min_instances" {
  type        = number
  description = "Minimum Cloud Run instances for the API (0 = scale-to-zero, 1 = always-warm / no cold starts)"
  default     = 0
}

variable "api_max_instances" {
  type        = number
  description = "Maximum Cloud Run instances for the API"
  default     = 10
}

variable "webui_min_instances" {
  type        = number
  description = "Minimum Cloud Run instances for the WebUI"
  default     = 0
}

variable "webui_max_instances" {
  type        = number
  description = "Maximum Cloud Run instances for the WebUI"
  default     = 3
}
