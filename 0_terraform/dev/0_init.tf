terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.82.0"
    }
  }

  cloud {
    organization = "teragonia"

    workspaces {
      tags = ["idso2305llms-chatapp", "dev"]
    }
  }
}

provider "google" {
  project = var.GCP_PROJECT_ID
  region  = var.REGION
  zone    = var.ZONE
}

# Provides access to the google provider's metadata for other resources to use.
data "google_client_config" "provider" {}