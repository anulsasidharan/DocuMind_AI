# FastAPI backend — Cloud Run v2 service.
# Secrets are mounted as environment variables from Secret Manager latest version.

resource "google_cloud_run_v2_service" "api" {
  project  = var.project_id
  name     = "documind-api"
  location = var.region
  labels   = local.labels

  template {
    service_account = google_service_account.documind_api.email

    scaling {
      min_instance_count = var.api_min_instances
      max_instance_count = var.api_max_instances
    }

    containers {
      image = var.api_image

      resources {
        limits = {
          cpu    = "2"
          memory = "4Gi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      # Non-secret configuration
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "GCS_BUCKET_DOCS"
        value = var.gcs_bucket_docs
      }
      env {
        name  = "COLLECTION_NAME"
        value = var.collection_name
      }
      env {
        name  = "LOG_LEVEL"
        value = "INFO"
      }

      # Secrets injected from Secret Manager
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

      ports {
        container_port = 8000
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 10
        period_seconds        = 5
        failure_threshold     = 10
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        period_seconds    = 30
        failure_threshold = 3
      }
    }
  }

  depends_on = [
    google_project_service.required_apis,
    google_service_account.documind_api,
    google_secret_manager_secret.openai_api_key,
    google_secret_manager_secret.qdrant_url,
    google_secret_manager_secret.qdrant_api_key,
  ]
}

# Allow unauthenticated invocations so external clients can reach the API.
# Restrict this (remove the binding) if you want IAM-protected endpoints.
resource "google_cloud_run_v2_service_iam_member" "api_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.api.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
