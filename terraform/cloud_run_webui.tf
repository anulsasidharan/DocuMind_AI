# Streamlit WebUI — same Docker image as the API, command overridden at runtime.

resource "google_cloud_run_v2_service" "webui" {
  project  = var.project_id
  name     = "documind-webui"
  location = var.region
  labels   = local.labels

  template {
    service_account = google_service_account.documind_api.email

    scaling {
      min_instance_count = var.webui_min_instances
      max_instance_count = var.webui_max_instances
    }

    containers {
      image   = var.webui_image
      command = ["streamlit"]
      args = [
        "run",
        "ui/streamlit_app.py",
        "--server.port=8080",
        "--server.address=0.0.0.0",
        "--server.headless=true",
      ]

      resources {
        limits = {
          cpu    = "1"
          memory = "2Gi"
        }
        cpu_idle          = true
        startup_cpu_boost = true
      }

      # Point the UI at the deployed API
      env {
        name  = "DOCUMIND_API_URL"
        value = google_cloud_run_v2_service.api.uri
      }
      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      ports {
        container_port = 8080
      }

      startup_probe {
        http_get {
          path = "/_stcore/health"
          port = 8080
        }
        initial_delay_seconds = 15
        period_seconds        = 5
        failure_threshold     = 12
      }
    }
  }

  depends_on = [
    google_cloud_run_v2_service.api,
    google_project_service.required_apis,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "webui_public" {
  project  = var.project_id
  location = var.region
  name     = google_cloud_run_v2_service.webui.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
