output "artifact_registry_url" {
    value = "${google_artifact_registry_repository.default-docker.location}-docker.pkg.dev/${var.GCP_PROJECT_ID}/${google_artifact_registry_repository.default-docker.name}"
}

output "postgres_db_ip" {
  value = google_sql_database_instance.postgres-db-instance.public_ip_address
}

# us-docker.pkg.dev/trg-d-i0523dsollms-chatapp/default-docker/2_svc_vectordb