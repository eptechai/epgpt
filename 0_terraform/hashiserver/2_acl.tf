## Allow listed ports between VMs.
resource "google_compute_firewall" "consul" {
  name    = "allow-consul-ports"
  network = var.vpc
  allow {
    protocol = "tcp"
    ports    = ["8500", "8600", "8503", "8301", "8302", "8300", "21000", "21255"]
  }
  allow {
    protocol = "icmp"
  }
  source_tags = ["hashistack-server", "hashistack-client"]
  target_tags = ["hashistack-server", "hashistack-client"]
}

resource "google_compute_firewall" "nomad" {
  name    = "allow-nomad-ports"
  network = var.vpc
  allow {
    protocol = "tcp"
    ports    = ["4646", "4647"]
  }
  source_tags = ["hashistack-server", "hashistack-client"]
  target_tags = ["hashistack-server"]
}

resource "google_compute_firewall" "nomad_interserver" {
  name    = "allow-nomad-interserver-ports"
  network = var.vpc
  allow {
    protocol = "tcp"
    ports    = ["4648"]
  }
  allow {
    protocol = "udp"
    ports    = ["4648"]
  }
  source_tags = ["hashistack-server"]
  target_tags = ["hashistack-server"]
}
