resource "google_storage_bucket" "vectordb_indexes_global" {
  name                     = "trg-${var.GCP_PROJECT_ID}-vectordb-indexes-global"
  location             = var.REGION
  public_access_prevention = "enforced"
}