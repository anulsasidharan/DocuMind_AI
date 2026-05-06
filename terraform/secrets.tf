# Secret Manager containers — values are set manually after `terraform apply`.
# Each secret is a placeholder; actual payloads are added via the GCP Console
# or `gcloud secrets versions add` (see deployment guide).

resource "google_secret_manager_secret" "openai_api_key" {
  project   = var.project_id
  secret_id = "documind-openai-api-key"
  labels    = local.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret" "qdrant_url" {
  project   = var.project_id
  secret_id = "documind-qdrant-url"
  labels    = local.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}

resource "google_secret_manager_secret" "qdrant_api_key" {
  project   = var.project_id
  secret_id = "documind-qdrant-api-key"
  labels    = local.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.required_apis]
}
