variable "GCP_PROJECT_ID" {
  type        = string
  description = "GCP Project ID"
}

variable "GOOGLE_CREDENTIALS" {
  type        = string
  sensitive   = true
  description = "JSON Service Account Key for a service account to be used by Terraform. Best provided in Terraform Cloud's Environment Variables."
}

variable "REGION" {
  description = "Google Cloud region for the VPC"
  default     = "us-central1"
}

variable "BACKUP_REGION" {
  description = "Google Cloud region for the Database backup"
  default     = "us-central1"
}

variable "ZONE" {
  description = "Google Cloud zone for the VPC"
  default     = "us-central1-a"
}

variable "SUBNET_IP_RANGE" {
  description = "IP range for the VPC subnet"
  type        = string
}

variable "DOPPLER_TOKEN" {
  type        = string
  description = "Doppler Service Token to be used by the application. Best provided in Terraform Cloud's Environment Variables."
}

variable "DATABASE_NAME" {
  type        = string
  description = "Name of the database to be created"
}

variable "DATABASE_USER_PASSWORD" {
  type        = string
  description = "Password for the database user"
}