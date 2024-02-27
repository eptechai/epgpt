resource "google_sql_database_instance" "postgres-db-instance" {
  name             = "${var.GCP_PROJECT_ID}-postgres"
  region           = var.REGION
  database_version = "POSTGRES_15"

  settings {
    tier = "db-f1-micro"

    ip_configuration {
      ipv4_enabled = true
      require_ssl = true
    }

    backup_configuration {
      enabled    = true
      start_time = "07:00"
      location   = var.BACKUP_REGION
      backup_retention_settings {
        retention_unit   = "COUNT"
        retained_backups = 15
      }
    }

    insights_config {
      query_insights_enabled = true
      query_plans_per_minute = 5
      query_string_length = 1024
      record_application_tags = false
      record_client_address = false
    }

    database_flags {
      name = "max_connections"
      value = 200
    }
  }

  # set `deletion_protection` to true, will ensure that one cannot accidentally delete this instance by
  # use of Terraform whereas `deletion_protection_enabled` flag protects this instance at the GCP level.
  deletion_protection = true
}


resource "google_sql_database" "database" {
  name     = var.DATABASE_NAME
  instance = google_sql_database_instance.postgres-db-instance.name
}


resource "google_sql_user" "user" {
  name     = "ci-user"
  instance = google_sql_database_instance.postgres-db-instance.name
  password = var.DATABASE_USER_PASSWORD
}

resource "google_project_iam_member" "cloudsql_client" {
  project = var.GCP_PROJECT_ID
  role    = "roles/cloudsql.client" // TODO: Apply an IAM policy to further restrict to one specific database instance.
  member  = google_service_account.svc_app.member
  
}