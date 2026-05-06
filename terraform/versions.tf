terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  # Recommended for team / CI workflows: store state in GCS.
  # 1. Create a bootstrap bucket first (once):
  #    gsutil mb -p PROJECT_ID -l REGION gs://PROJECT_ID-tf-state
  # 2. Uncomment the block below and run: terraform init -migrate-state
  #
  # backend "gcs" {
  #   bucket = "PROJECT_ID-tf-state"
  #   prefix = "documind-ai/state"
  # }
}
