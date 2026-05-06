# GCS bucket that stores uploaded source documents.
# Versioning is enabled so accidental overwrites can be recovered.

resource "google_storage_bucket" "docs" {
  project       = var.project_id
  name          = var.gcs_bucket_docs
  location      = var.region
  force_destroy = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      # Remove non-current versions older than 30 days to control storage costs.
      days_since_noncurrent_time = 30
      with_state                 = "ARCHIVED"
    }
  }

  labels = local.labels

  depends_on = [google_project_service.required_apis]
}
