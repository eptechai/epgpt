# Service Account for the Hashistack VMs.
resource "google_service_account" "svc_hashistack_servers" {
  account_id  = "svc-hashistack-servers"
  description = "Service Account for Hashistack VMs"
}

resource "google_project_iam_member" "svc_hashistack_servers_logging_logWriter" {
  project = var.gcp_project_id
  role    = "roles/logging.logWriter"
  member  = google_service_account.svc_hashistack_servers.member
}

resource "google_project_iam_member" "svc_hashistack_servers_monitoring_metricWriter" {
  project = var.gcp_project_id
  role    = "roles/monitoring.metricWriter"
  member  = google_service_account.svc_hashistack_servers.member
}

resource "google_project_iam_member" "svc_hashistack_servers_compute_viewer" {
  project = var.gcp_project_id
  role    = "roles/compute.viewer"
  member  = google_service_account.svc_hashistack_servers.member
}