resource "google_service_account" "svc_dss" {
  account_id  = "svc-dss"
  description = "Used by Dataiku to write data to the objects."
}

resource "google_storage_bucket_iam_member" "svc_dss_gcs_vectordb_indexes_global" {
  bucket = google_storage_bucket.vectordb_indexes_global.name
  role   = "roles/storage.admin"
  member = google_service_account.svc_dss.member
  
}
