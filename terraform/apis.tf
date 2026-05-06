# Enable all GCP APIs required by DocuMind AI.
# disable_on_destroy = false prevents accidental API disablement on terraform destroy.

resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",                  # Cloud Run
    "storage.googleapis.com",              # Cloud Storage (GCS)
    "secretmanager.googleapis.com",        # Secret Manager
    "artifactregistry.googleapis.com",     # Artifact Registry (Docker images)
    "cloudbuild.googleapis.com",           # Cloud Build (optional CI/CD)
    "iam.googleapis.com",                  # IAM
    "cloudresourcemanager.googleapis.com", # Resource Manager (IAM lookups)
    "logging.googleapis.com",              # Cloud Logging
    "monitoring.googleapis.com",           # Cloud Monitoring
  ])

  project            = var.project_id
  service            = each.key
  disable_on_destroy = false
}
