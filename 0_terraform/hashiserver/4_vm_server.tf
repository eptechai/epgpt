resource "google_compute_address" "hashistack" {
  count = length(var.zones)
  name         = "hashistack-server-${count.index + 1}"
  subnetwork   = var.subnet
  address_type = "INTERNAL"
  region       = var.region
}


resource "google_compute_instance" "hashistack" {
  count = length(var.zones)
  name  = "${var.gcp_project_id}-hashistack-server-${count.index + 1}"
  lifecycle {
    ignore_changes = [
      boot_disk[0].initialize_params[0].image, # Bug with Ubuntu Pro images where provider tries to replace them.
      metadata["ssh-keys"],                    # Terraform tries to eliminate temporary SSH keys provisioned via IAP.
    ]
  }

  boot_disk {
    auto_delete = true
    device_name = "${var.gcp_project_id}-hashistack-server-${count.index + 1}-disk"

    initialize_params {
      image = "ubuntu-os-pro-cloud/ubuntu-pro-2204-lts"
      size  = 40
      type  = "pd-balanced"
    }
  }

  machine_type = "e2-medium"

  network_interface {
    subnetwork = var.subnet
    network_ip = google_compute_address.hashistack[count.index].address
  }

  service_account {
    email  = google_service_account.svc_hashistack_servers.email
    scopes = ["cloud-platform"]
  }

  tags = ["hashistack-server"]
  zone = var.zones[count.index]
}
