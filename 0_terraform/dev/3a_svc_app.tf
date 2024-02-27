resource "google_service_account" "svc_app" {
  account_id  = "svc-app"
  description = "Used by the app to access GCP services"
}

resource "google_storage_bucket_iam_member" "svc_app_gcs_vectordb_indexes_global" {
  bucket = google_storage_bucket.vectordb_indexes_global.name
  role   = "roles/storage.objectViewer"
  member = google_service_account.svc_app.member
}

# IAM Binding to Kubernetes
resource "google_service_account_iam_member" "workloadIdentityUser" {
  service_account_id = google_service_account.svc_app.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.GCP_PROJECT_ID}.svc.id.goog[default/svc-app]"
}

resource "google_storage_bucket_iam_member" "svc_app_gcs_file_uploads" {
  bucket = google_storage_bucket.file-uploads.name
  role   = "roles/storage.admin"
  member = google_service_account.svc_app.member
}

resource "google_storage_bucket_iam_member" "svc_app_gcs_indices" {
  bucket = google_storage_bucket.indices.name
  role   = "roles/storage.admin"
  member = google_service_account.svc_app.member
}

resource "google_storage_bucket_iam_member" "svc_app_gcs_peft_adapters" {
  bucket = google_storage_bucket.peft-adapters.name
  role   = "roles/storage.admin"
  member = google_service_account.svc_app.member
}

resource "google_storage_bucket_iam_member" "svc_app_gcs_corpus_files" {
  bucket = google_storage_bucket.corpus-files.name
  role   = "roles/storage.admin"
  member = google_service_account.svc_app.member
}

resource "google_storage_bucket_iam_member" "svc_app_gcs_corpus_indices" {
  bucket = google_storage_bucket.corpus-indices.name
  role   = "roles/storage.admin"
  member = google_service_account.svc_app.member
}

resource "google_storage_bucket_iam_member" "svc_app_gcs_merged_indices" {
  bucket = google_storage_bucket.merged-indices.name
  role   = "roles/storage.admin"
  member = google_service_account.svc_app.member
}

resource "google_project_iam_member" "log_writer" {
  project = var.GCP_PROJECT_ID
  role    = "roles/logging.logWriter"
  member  = google_service_account.svc_app.member
}
