# DocuMind AI — Terraform entry point
#
# Resources are split across focused files:
#   apis.tf              — GCP API enablement
#   iam.tf               — Service account + IAM bindings
#   secrets.tf           — Secret Manager containers
#   gcs.tf               — GCS bucket for source documents
#   artifact_registry.tf — Docker image repository
#   cloud_run_api.tf     — FastAPI Cloud Run service
#   cloud_run_webui.tf   — Streamlit Cloud Run service
#   outputs.tf           — Useful post-apply values
#
# Prerequisites (run once before terraform init):
#   gcloud auth application-default login
#   gcloud config set project YOUR_PROJECT_ID
#   gsutil mb -p YOUR_PROJECT_ID -l us-central1 gs://YOUR_PROJECT_ID-tf-state
#
# To enable remote state (recommended for teams):
#   1. Uncomment the backend block in versions.tf
#   2. Run: terraform init -migrate-state
