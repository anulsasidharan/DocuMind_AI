# DocuMind AI — Terraform root (expand in GCP phase: Cloud Run, GCS, IAM).
terraform {
  required_version = ">= 1.5.0"
}

variable "project_id" {
  type        = string
  description = "GCP project ID"
  default     = ""
}

output "placeholder" {
  value = "Add google provider, Cloud Run, and GCS resources in later phases."
}
