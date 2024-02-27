resource "google_storage_bucket" "vectordb_indexes_global" {
  name                     = "trg-${var.GCP_PROJECT_ID}-vectordb-indexes-global"
  location                 = var.REGION
  public_access_prevention = "enforced"
}

resource "google_storage_bucket" "file-uploads" {
  name                     = "${var.GCP_PROJECT_ID}-file-uploads"
  location                 = var.REGION
  public_access_prevention = "enforced"
}

resource "google_storage_bucket" "indices" {
  name                     = "${var.GCP_PROJECT_ID}-indices"
  location                 = var.REGION
  public_access_prevention = "enforced"
}

resource "google_storage_bucket" "peft-adapters" {
  name                     = "${var.GCP_PROJECT_ID}-peft-adapters"
  location                 = var.REGION
  public_access_prevention = "enforced"
}

resource "google_storage_bucket" "corpus-files" {
  name                     = "${var.GCP_PROJECT_ID}-corpus-files"
  location                 = var.REGION
  public_access_prevention = "enforced"
}

resource "google_storage_bucket" "corpus-indices" {
  name                     = "${var.GCP_PROJECT_ID}-corpus-indices"
  location                 = var.REGION
  public_access_prevention = "enforced"
}

resource "google_storage_bucket" "merged-indices" {
  name                     = "${var.GCP_PROJECT_ID}-merged-indices"
  location                 = var.REGION
  public_access_prevention = "enforced"
}
