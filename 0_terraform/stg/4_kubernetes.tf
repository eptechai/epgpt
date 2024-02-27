resource "google_container_cluster" "default" {
  name     = "${var.GCP_PROJECT_ID}-gke"
  location = var.REGION

  network    = google_compute_network.default.name
  subnetwork = google_compute_subnetwork.default.name

  # Enabling Autopilot for this cluster
  enable_autopilot = true
  cluster_autoscaling {
    auto_provisioning_defaults {
      oauth_scopes = [
        "https://www.googleapis.com/auth/cloud-platform",
      ]
      service_account = google_service_account.svc_gke.email
    }
  }
}

module "gke_auth" {
  source               = "terraform-google-modules/kubernetes-engine/google//modules/auth"
  project_id           = var.GCP_PROJECT_ID
  cluster_name         = google_container_cluster.default.name
  location             = google_container_cluster.default.location
  use_private_endpoint = false
}

resource "local_file" "kubeconfig" {
  content  = module.gke_auth.kubeconfig_raw
  filename = "${path.module}/generated/kubeconfig"
}