## OUT-OF-BAND CONFIGURATION REQUIRED: Go into the Kubernetes cluster, 
## find the Doppler token secret, and pass in an actual Doppler token.

provider "helm" {
  kubernetes {
    host                   = google_container_cluster.default.endpoint
    token                  = data.google_client_config.provider.access_token
    cluster_ca_certificate = base64decode(google_container_cluster.default.master_auth.0.cluster_ca_certificate)
  }
}

# resource "helm_release" "default" {
#   name  = "idso2305llms-chatapp"
#   chart = "generated/helmchart"

#   values = [
#     file("${path.module}/generated/helmchart/values.yaml"),     # Base (parent) values.yaml
#     file("${path.module}/generated/helmchart/stg.values.yaml"), # Layered values.yaml that overrides the base.
#   ]

#   set_sensitive {
#     name  = "dopplerSecret.serviceToken"
#     value = var.DOPPLER_TOKEN
#   }
# }
