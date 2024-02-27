resource "google_service_account" "svc_app" {
  account_id  = "svc-app"
  description = "Used by the app to access GCP services"
}

resource "google_service_account" "svc_gke" {
  account_id  = "svc-gke"
  description = "Used by GKE Clusters"
}


resource "google_storage_bucket_iam_binding" "svc_app_gcs_vectordb_indexes_global" {
  bucket = google_storage_bucket.vectordb_indexes_global.name
  role   = "roles/storage.objectViewer"
  members = [
    google_service_account.svc_app.member,
  ]
}

resource "google_project_iam_binding" "monitoring_metricWriter" {
  project = var.GCP_PROJECT_ID
  role    = "roles/monitoring.metricWriter"
  members = [
    google_service_account.svc_app.member,
    google_service_account.svc_gke.member,
  ]
}

resource "google_project_iam_binding" "logging_logWriter" {
  project = var.GCP_PROJECT_ID
  role    = "roles/logging.logWriter"
  members = [
    google_service_account.svc_app.member,
    google_service_account.svc_gke.member,
  ]
}
