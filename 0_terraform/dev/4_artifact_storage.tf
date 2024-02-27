# Artifact Registry
resource "google_artifact_registry_repository" "default-docker" {
  repository_id = "default-docker"
  location      = "us"
  format        = "DOCKER"
}

resource "google_service_account" "svc_cicd" {
  account_id  = "svc-cicd"
  description = "Used by the CICD Pipeline."
}

resource "google_service_account_iam_member" "svc_cicd_keyAdmin" {
  service_account_id = google_service_account.svc_cicd.name
  role               = "roles/iam.serviceAccountKeyAdmin"
  member             = "serviceAccount:svc-doppler@trg-p-bootstrap.iam.gserviceaccount.com"
}


resource "google_artifact_registry_repository_iam_member" "default-docker-writers" {
  project    = google_artifact_registry_repository.default-docker.project
  location   = google_artifact_registry_repository.default-docker.location
  repository = google_artifact_registry_repository.default-docker.name
  role       = "roles/artifactregistry.repoAdmin"
  member     = google_service_account.svc_cicd.member
}

resource "google_compute_global_address" "default" {
  name = "chatapp"
}