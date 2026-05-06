# Docker repository in Artifact Registry — stores API and WebUI images.
# Both services use the same image; the WebUI overrides the command at runtime.

resource "google_artifact_registry_repository" "documind" {
  project       = var.project_id
  location      = var.region
  repository_id = "documind"
  format        = "DOCKER"
  description   = "DocuMind AI container images"
  labels        = local.labels

  depends_on = [google_project_service.required_apis]
}
