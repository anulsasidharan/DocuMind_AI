# Copy this file to terraform.tfvars and fill in your values.
# Never commit terraform.tfvars — it contains your project ID.

# ── Required ──────────────────────────────────────────────────────────────────

project_id      = "documindai-495505"
gcs_bucket_docs = "documindai-bucket"

# Fill these in after: docker build → docker push → copy the full image URL
api_image   = "us-central1-docker.pkg.dev/documindai-495505/documind/api:latest"
webui_image = "us-central1-docker.pkg.dev/documindai-495505/documind/api:latest"
#api_image    = ""
#webui_image  = ""

# ── Optional (change only if needed) ─────────────────────────────────────────

region          = "us-central1"
collection_name = "documindai"
environment     = "production"

api_min_instances  = 0   # 0 = scale-to-zero (saves cost); 1 = always warm
api_max_instances  = 10
webui_min_instances = 0
webui_max_instances = 3
