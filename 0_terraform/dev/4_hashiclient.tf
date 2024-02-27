resource "google_service_account" "svc_hashistack_client" {
  account_id  = "svc-hashistack-clients"
  description = "Service Account for Hashistack Client VMs"
}

resource "google_project_iam_member" "svc_hashistack_client_logging_logWriter" {
  project = var.GCP_PROJECT_ID
  role    = "roles/logging.logWriter"
  member  = google_service_account.svc_hashistack_client.member
}

resource "google_project_iam_member" "svc_hashistack_client_monitoring_metricWriter" {
  project = var.GCP_PROJECT_ID
  role    = "roles/monitoring.metricWriter"
  member  = google_service_account.svc_hashistack_client.member
}

resource "google_project_iam_member" "svc_hashistack_client_compute_viewer" {
  project = var.GCP_PROJECT_ID
  role    = "roles/compute.viewer"
  member  = google_service_account.svc_hashistack_client.member
}

resource "google_artifact_registry_repository_iam_member" "svc_hashistack_client_artifactregistry_reader" {
  project    = google_artifact_registry_repository.default-docker.project
  location   = google_artifact_registry_repository.default-docker.location
  repository = google_artifact_registry_repository.default-docker.name
  role       = "roles/artifactregistry.reader"
  member     = google_service_account.svc_hashistack_client.member
}

locals {
  hashiclient_zones = ["us-central1-a"]
}

resource "google_compute_address" "hashistack" {
  count        = length(local.hashiclient_zones)
  name         = "hashistack-client-${count.index + 1}"
  subnetwork   = google_compute_subnetwork.default.name
  address_type = "INTERNAL"
  region       = var.REGION
}


resource "google_compute_instance" "hashistack" {
  count = length(local.hashiclient_zones)
  name  = "${var.GCP_PROJECT_ID}-hashistack-client-${count.index + 1}"
  lifecycle {
    ignore_changes = [
      boot_disk[0].initialize_params[0].image, # Bug with Ubuntu Pro images where provider tries to replace them.
      metadata["ssh-keys"],                    # Terraform tries to eliminate temporary SSH keys provisioned via IAP.
    ]
  }

  boot_disk {
    auto_delete = true
    device_name = "${var.GCP_PROJECT_ID}-hashistack-client-${count.index + 1}-disk"

    initialize_params {
      image = "ubuntu-os-pro-cloud/ubuntu-pro-2204-lts"
      size  = 100
      type  = "pd-balanced"
    }
  }

  machine_type = "n2d-highcpu-32"

  network_interface {
    subnetwork = google_compute_subnetwork.default.name
    network_ip = google_compute_address.hashistack[count.index].address
  }

  service_account {
    email  = google_service_account.svc_hashistack_client.email
    scopes = ["cloud-platform"]
  }

  tags = ["hashistack-client"]
  zone = local.hashiclient_zones[count.index]
}
