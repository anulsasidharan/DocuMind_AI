output "api_url" {
  description = "Cloud Run URL for the FastAPI backend"
  value       = google_cloud_run_v2_service.api.uri
}

output "webui_url" {
  description = "Cloud Run URL for the Streamlit WebUI"
  value       = google_cloud_run_v2_service.webui.uri
}

output "gcs_bucket_docs" {
  description = "GCS bucket name for uploaded documents"
  value       = google_storage_bucket.docs.name
}

output "artifact_registry_repo" {
  description = "Artifact Registry repository URL (use as docker push prefix)"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/documind"
}

output "service_account_email" {
  description = "Service account email used by Cloud Run services"
  value       = google_service_account.documind_api.email
}

output "secret_names" {
  description = "Secret Manager secret IDs — add secret versions after apply"
  value = {
    openai_api_key = google_secret_manager_secret.openai_api_key.secret_id
    qdrant_url     = google_secret_manager_secret.qdrant_url.secret_id
    qdrant_api_key = google_secret_manager_secret.qdrant_api_key.secret_id
  }
}
