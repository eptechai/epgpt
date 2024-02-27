# reserved IP address
resource "google_compute_global_address" "ext-ip" {
  name = "${var.GCP_PROJECT_ID}-ext-ip"
}

# http forwarding rule
resource "google_compute_global_forwarding_rule" "http-forwarding-rule" {
  name                  = "${var.GCP_PROJECT_ID}-http-forwarding-rule"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range            = "80"
  target                = google_compute_target_http_proxy.http-proxy.id
  ip_address            = google_compute_global_address.ext-ip.id
}

# http proxy
resource "google_compute_target_http_proxy" "http-proxy" {
  name    = "${var.GCP_PROJECT_ID}-http-to-https-redirect-proxy"
  url_map = google_compute_url_map.http-url-map.id
}

# http url map
resource "google_compute_url_map" "http-url-map" {
  name = "${var.GCP_PROJECT_ID}-http-url-map"
  default_url_redirect {
    https_redirect = true
    strip_query    = false
  }
}

# https forwarding rule
resource "google_compute_global_forwarding_rule" "https-forwarding-rule" {
  name                  = "${var.GCP_PROJECT_ID}-https-forwarding-rule"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL"
  port_range            = "443"
  target                = google_compute_target_https_proxy.https-proxy.id
  ip_address            = google_compute_global_address.ext-ip.id
}

# ssl certificate
resource "google_compute_managed_ssl_certificate" "https-ssl-cert" {
  name = "${var.GCP_PROJECT_ID}-https-ssl-cert"

  managed {
    domains = ["aichat.dev.teragonia.com"]
  }
}

# https proxy
resource "google_compute_target_https_proxy" "https-proxy" {
  name             = "${var.GCP_PROJECT_ID}-https-proxy"
  url_map          = google_compute_url_map.https-url-map.id
  ssl_certificates = [google_compute_managed_ssl_certificate.https-ssl-cert.id]
}


# url map
resource "google_compute_url_map" "https-url-map" {
  name            = "${var.GCP_PROJECT_ID}-https-url-map"
  default_service = google_compute_backend_service.backend-service.id
}

# backend service with custom request and response headers
resource "google_compute_backend_service" "backend-service" {
  name                  = "${var.GCP_PROJECT_ID}-backend-service"
  protocol              = "HTTP"
  port_name             = "http"
  load_balancing_scheme = "EXTERNAL"
  timeout_sec           = 600
  enable_cdn            = false
  health_checks         = [google_compute_health_check.health-check.id]

  dynamic "backend" {
    for_each = google_compute_instance_group.hashiclient_groups[*]
    content {
      group           = google_compute_instance_group.hashiclient_groups[backend.key].self_link
      balancing_mode  = "UTILIZATION"
      capacity_scaler = 1.0
    }
  }
}

# health check
resource "google_compute_health_check" "health-check" {
  name = "${var.GCP_PROJECT_ID}-health-check"

  timeout_sec        = 1
  check_interval_sec = 1

  tcp_health_check {
    port_name = "http"
  }
}

resource "google_compute_instance_group" "hashiclient_groups" {
  count       = length(local.hashiclient_zones)
  name        = "${var.GCP_PROJECT_ID}-hashiclient-group-${count.index + 1}"
  description = "Hashiclient Instance Group"

  instances = [
    google_compute_instance.hashistack[count.index].self_link
  ]

  named_port {
    name = "http"
    port = "4180"
  }

  zone = local.hashiclient_zones[count.index]
}
