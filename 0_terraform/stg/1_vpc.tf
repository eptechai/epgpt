resource "google_compute_network" "default" {
  name                    = "${var.GCP_PROJECT_ID}-vpc"
  auto_create_subnetworks = false
}


resource "google_compute_subnetwork" "default" {
  name          = "${var.GCP_PROJECT_ID}-subnet"
  network       = google_compute_network.default.self_link
  ip_cidr_range = var.SUBNET_IP_RANGE
}

# https://cloud.google.com/architecture/building-internet-connectivity-for-private-vms

resource "google_compute_router" "default" {
  name    = "${var.GCP_PROJECT_ID}-router"
  network = google_compute_network.default.name
}

resource "google_compute_router_nat" "default" {
  name                               = "${var.GCP_PROJECT_ID}-nat-config"
  router                             = google_compute_router.default.name
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_PRIMARY_IP_RANGES"
}