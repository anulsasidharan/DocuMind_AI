# Service account used by both Cloud Run services.
# Permissions are additive — only the minimum required roles are granted.

resource "google_service_account" "documind_api" {
  project      = var.project_id
  account_id   = "documind-api-sa"
  display_name = "DocuMind AI — Cloud Run service account"

  depends_on = [google_project_service.required_apis]
}

# ── GCS ─────────────────────────────────────────────────────────────────────

resource "google_storage_bucket_iam_member" "api_gcs_object_admin" {
  bucket = google_storage_bucket.docs.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.documind_api.email}"
}

# ── Secret Manager ───────────────────────────────────────────────────────────

resource "google_secret_manager_secret_iam_member" "api_openai_key" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.openai_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.documind_api.email}"
}

resource "google_secret_manager_secret_iam_member" "api_qdrant_url" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.qdrant_url.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.documind_api.email}"
}

resource "google_secret_manager_secret_iam_member" "api_qdrant_key" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.qdrant_api_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.documind_api.email}"
}

# ── Cloud Logging ─────────────────────────────────────────────────────────────

resource "google_project_iam_member" "api_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.documind_api.email}"
}

resource "google_project_iam_member" "api_metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.documind_api.email}"
}
