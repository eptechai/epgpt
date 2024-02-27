resource "google_service_account" "svc_doppler" {
  account_id  = "svc-doppler"
  description = "doppler_impersonate:OoS61AsjEpMDA" # Description is set by Doppler, do not modify.
}

resource "google_service_account_iam_member" "svc_doppler_viewer" {
  service_account_id = google_service_account.svc_doppler.name
  role               = "roles/iam.serviceAccountViewer"
  member             = "serviceAccount:operator@doppler-integrations.iam.gserviceaccount.com"
}

resource "google_service_account_iam_member" "svc_doppler_tokenCreator" {
  service_account_id = google_service_account.svc_doppler.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:operator@doppler-integrations.iam.gserviceaccount.com"
}
