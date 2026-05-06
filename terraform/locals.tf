locals {
  # Base URL for Artifact Registry — used in outputs and documentation
  artifact_registry_base = "${var.region}-docker.pkg.dev/${var.project_id}/documind"

  # Standard labels applied to every resource
  labels = {
    app         = "documind-ai"
    environment = var.environment
    managed_by  = "terraform"
  }
}
