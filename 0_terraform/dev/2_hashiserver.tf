module "hashistack-servers" {
  source         = "../hashiserver"
  region         = var.REGION
  gcp_project_id = var.GCP_PROJECT_ID
  zones          = ["us-central1-a", "us-central1-b", "us-central1-c"]
  vpc            = google_compute_network.default.name
  subnet         = google_compute_subnetwork.default.name
}
