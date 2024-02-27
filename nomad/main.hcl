variable "replicas" {
  type = number
  default = 1
}
variable "doppler_token" {}
variable "oauth2proxy_image" {}
variable "frontend_image" {}
variable "backend_image" {}
variable "svc_vectordb_global_image" {}
variable "svc_vectordb_convo_image" {}
variable "index_builder_image" {}
variable "query_engine_image" {}
variable "response_synthesizer_image" {}

# This declares a job named "docs". There can be exactly one
# job declaration per job file.
job "idso2305llms-app-dev" {
  // address = "127.0.0.1:5656"

  # Run this job as a "service" type. Each job type has different
  # properties. See the documentation below for more examples.
  type = "service"

  group "oauth2proxy" {
    count = var.replicas
    meta {
      reeval = uuidv4()
    }
    network {
      mode = "bridge"
      port "http" {
        static = 4180
        to     = 4179
      }
    }

    update {
      max_parallel     = 1
      min_healthy_time = "30s"
      healthy_deadline = "2m"
      auto_revert      = true
    }


    service {
      name = "oauth2proxy"
      port = "http"

      check {
        type     = "http"
        path     = "/ping"
        interval = "10s"
        timeout  = "2s"
      }

      connect {
        sidecar_service {
          proxy {
            local_service_port = 4179
            upstreams {
              destination_name = "frontend"
              local_bind_port  = 3000
            }
            upstreams {
              destination_name = "backend"
              local_bind_port  = 8000
            }
            expose {
              path {
                path            = "/"
                protocol        = "http"
                local_path_port = 4179
                listener_port   = "http"
              }
            }
          }
        }
      }
    }

    task "doppler" {
      driver = "docker"
      lifecycle {
        hook    = "prestart"
        sidecar = false
      }
      config {
        image          = "dopplerhq/cli:3"
        auth_soft_fail = true
        entrypoint     = ["/bin/sh", "-c"]
        command        = "doppler --config-dir /secrets/doppler secrets download --no-file --format env | grep -e OAUTH2_PROXY_CLIENT_SECRET -e OAUTH2_PROXY_COOKIE_SECRET > ${NOMAD_ALLOC_DIR}/doppler.env"
      }
      env {
        DOPPLER_TOKEN = var.doppler_token
      }
    }

    task "oauth2proxy" {
      driver = "docker"

      config {
        image          = var.oauth2proxy_image
        force_pull     = true
        auth_soft_fail = true
        ports          = ["http"]
      }

      resources {
        cpu    = 500 # MHz
        memory = 128 # MB
      }

      template {
        source      = "${NOMAD_ALLOC_DIR}/doppler.env"
        destination = "${NOMAD_SECRETS_DIR}/doppler.env"
        env         = true
      }

      env {
        OAUTH2_PROXY_HTTP_ADDRESS              = "0.0.0.0:4179"
        OAUTH2_PROXY_UPSTREAMS                 = "http://localhost:3000/,http://localhost:8000/api/" // TODO: Parameterize this.
        OAUTH2_PROXY_PROVIDER_DISPLAY_NAME     = "Auth0"
        OAUTH2_PROXY_PROVIDER                  = "oidc"
        OAUTH2_PROXY_OIDC_ISSUER_URL           = "https://teragonia.us.auth0.com/" // TODO: Parameterize this.
        OAUTH2_PROXY_CLIENT_ID                 = "RipbTIselesXcgXJKcZd4dN9aVRkXL5I"
        OAUTH2_PROXY_EMAIL_DOMAINS             = "*"
        OAUTH2_PROXY_PASS_ACCESS_TOKEN         = "true"
        OAUTH2_PROXY_COOKIE_SECURE             = "true"
        OAUTH2_PROXY_CUSTOM_TEMPLATES_DIR      = "/templates"
        OAUTH2_PROXY_PASS_AUTHORIZATION_HEADER = "true"
        OAUTH2_PROXY_SKIP_OIDC_DISCOVERY       = "true"
        OAUTH2_PROXY_REDEEM_URL                = "https://teragonia.us.auth0.com/oauth/token"                                                          // TODO: Parameterize this.
        OAUTH2_PROXY_LOGIN_URL                 = "https://teragonia.us.auth0.com/authorize?audience=https://teragonia.us.auth0.com/api/v2/" // TODO: Parameterize this.
        OAUTH2_PROXY_OIDC_JWKS_URL             = "https://teragonia.us.auth0.com/.well-known/jwks.json"                                                // TODO: Parameterize this.
        OAUTH2_PROXY_STANDARD_LOGGING          = "true"
        OAUTH2_PROXY_STANDARD_LOGGING_FORMAT   = "[{{.Timestamp}}] [{{.File}}] {{.Message}}"
        OAUTH2_PROXY_REQUEST_LOGGING           = "true"
        OAUTH2_PROXY_REQUEST_LOGGING_FORMAT    = "{{.Client}} - {{.Username}} [{{.Timestamp}}] {{.Host}} {{.RequestMethod}} {{.Upstream}} {{.RequestURI}} {{.Protocol}} {{.UserAgent}} {{.StatusCode}} {{.ResponseSize}} {{.RequestDuration}}"
        OAUTH2_PROXY_AUTH_LOGGING              = "true"
        OAUTH2_PROXY_AUTH_LOGGING_FORMAT       = "{{.Client}} - {{.Username}} [{{.Timestamp}}] [{{.Status}}] {{.Message}}"
        OAUTH2_FORCE_HTTPS                     = "true"
        OAUTH2_REDIRECT_URL = "https://aichat.dev.teragonia.com/oauth2/callback" // TODO: Parameterize this.
        OAUTH2_PROXY_UPSTREAM_TIMEOUT = "90s"
        OAUTH2_PROXY_COOKIE_EXPIRE = "23h"
      }
    }
  }

  group "frontend" {
    count = var.replicas
    meta {
      reeval = uuidv4()
    }
    network {
      mode = "bridge"
      port "http" {
        to = 3000
      }
    }

    update {
      max_parallel     = 1
      min_healthy_time = "30s"
      healthy_deadline = "2m"
      auto_revert      = true
    }

    service {
      name = "frontend"
      port = "http"

      check {
        type     = "http"
        path     = "/healthz"
        interval = "10s"
        timeout  = "2s"
      }

      connect {
        sidecar_service {
          proxy {
            local_service_port = 3000
          }
        }
      }
    }

    task "doppler" {
      driver = "docker"
      lifecycle {
        hook    = "prestart"
        sidecar = false
      }
      config {
        image          = "dopplerhq/cli:3"
        auth_soft_fail = true
        entrypoint     = ["/bin/sh", "-c"]
        command        = "doppler --config-dir /secrets/doppler secrets download --no-file --format env | grep -e PUBLIC_AUTH_0_END_SESSION_URL -e PUBLIC_AUTH_0_LOGOUT_REDIRECT_URL -e PUBLIC_AUTH_0_CLIENT_ID > ${NOMAD_ALLOC_DIR}/doppler.env"
      }
      env {
        DOPPLER_TOKEN = var.doppler_token
      }
    }

    task "frontend" {

      driver = "docker"

      config {
        image          = var.frontend_image
        force_pull     = true
        auth_soft_fail = true
        ports          = ["http"]
      }

      template {
        source      = "${NOMAD_ALLOC_DIR}/doppler.env"
        destination = "${NOMAD_SECRETS_DIR}/doppler.env"
        env         = true
      }

      resources {
        cpu    = 500 # MHz
        memory = 128 # MB
      }
    }
  }

  group "backend" {
    meta {
      reeval = uuidv4()
    }
    count = var.replicas
    network {
      mode = "bridge"
      port "http" {
        to = 8000
      }
    }

    update {
      max_parallel     = 1
      min_healthy_time = "30s"
      healthy_deadline = "2m"
      auto_revert      = true
    }

    service {
      name = "backend"
      port = "http"
      check {
        type     = "http"
        path     = "/api/health"
        interval = "10s"
        timeout  = "2s"
      }

      connect {
        sidecar_service {
          proxy {
            local_service_port = 8000
            upstreams {
              destination_name = "rabbitmq"
              local_bind_port  = 5672
            }
          }
        }
      }
    }

    task "doppler-sql-auth-proxy" {
      driver = "docker"
      lifecycle {
        hook    = "prestart"
        sidecar = false
      }
      config {
        image          = "dopplerhq/cli:3"
        auth_soft_fail = true
        entrypoint     = ["/bin/sh", "-c"]
        command        = "doppler --config-dir /secrets/doppler secrets get --plain GCP_SVC_APP_KEY > ${NOMAD_ALLOC_DIR}/gcp_svc_app_key.json"
      }
      env {
        INSTANCE_CONNECTION_NAME = "trg-d-i0523dsollms-chatapp:us-central1:trg-d-i0523dsollms-chatapp-postgres"
        DOPPLER_TOKEN            = var.doppler_token
      }
    }

    task "cloud-sql-auth-proxy" {
      driver = "docker"
      lifecycle {
        hook    = "prestart"
        sidecar = true
      }
      config {
        image          = "gcr.io/cloud-sql-connectors/cloud-sql-proxy:2.7.0"
        auth_soft_fail = true
        args = [
          "--structured-logs",
          "--port=5432",
          # TODO: Parameterize the cloud sql instance connection name.
          "trg-d-i0523dsollms-chatapp:us-central1:trg-d-i0523dsollms-chatapp-postgres",
        ]
      }
      env {
        GOOGLE_APPLICATION_CREDENTIALS = "${NOMAD_ALLOC_DIR}/gcp_svc_app_key.json"
      }
    }

    task "doppler" {
      driver = "docker"
      lifecycle {
        hook    = "prestart"
        sidecar = false
      }
      config {
        image          = "dopplerhq/cli:3"
        auth_soft_fail = true
        entrypoint     = ["/bin/sh", "-c"]
        command        = "doppler --config-dir /secrets/doppler secrets download --no-file --format env | grep -e DEBUG -e RABBITMQ_USERNAME -e RABBITMQ_PASSWORD -e OPENAI_KEY -e USER_FILES_BUCKET -e NEW_ATTACHMENT_QUEUE -e ATTACHMENT_STATUS_EXCHANGE -e AUTH_0_CLIENT_ID -e AUTH_0_USER_INFO_URL -e AUTH_0_JWKS_URL -e DATABASE_HOST -e DATABASE_PORT -e DATABASE_USER -e DATABASE_PASSWORD -e DATABASE_URL -e INDEX_DELETION_QUEUE -e CLOUD_STORAGE_CREDENTIALS -e GPU_CA_CERT_B64 -e GPU_CA_KEY_B64 -e INDEX_BUILDER_SERVICE_HOST -e QUERY_ENGINE_SERVICE_HOST -e RESPONSE_SYNTHESIZER_SERVICE_HOST > ${NOMAD_ALLOC_DIR}/doppler.env"

      }
      env {
        DOPPLER_TOKEN = var.doppler_token
      }
    }

    task "backend" {
      driver = "docker"

      config {
        image          = var.backend_image
        force_pull     = true
        auth_soft_fail = true
        ports          = ["http"]
      }

      template {
        source      = "${NOMAD_ALLOC_DIR}/doppler.env"
        destination = "${NOMAD_SECRETS_DIR}/doppler.env"
        env         = true
      }

      resources {
        cpu    = 1500 # MHz
        memory = 2048 # MB
      }

      env {
        RABBITMQHOST                      = "127.0.0.1"
        APPLICATION_DEFAULT_CREDENTIALS = "${NOMAD_ALLOC_DIR}/gcp_svc_app_key.json" 
      }
    }
  }

  group "rabbitmq" {
    count = 1
    network {
      mode = "bridge"
      port "amqp" {
        to = 5672
      }
    }

    service {
      name = "rabbitmq"
      port = "amqp"

      // TODO: Implement health checks for amqp protocol - need custom scripts.

      connect {
        sidecar_service {
          proxy {
            local_service_port = 5672
          }
        }
      }
    }

    task "doppler" {
      driver = "docker"
      lifecycle {
        hook    = "prestart"
        sidecar = false
      }
      config {
        image          = "dopplerhq/cli:3"
        auth_soft_fail = true
        entrypoint     = ["/bin/sh", "-c"]
        command        = "doppler --config-dir /secrets/doppler secrets download --no-file --format env | grep -e RABBITMQ_USERNAME -e RABBITMQ_PASSWORD -e MODEL_HOSTS | sed 's/RABBITMQ_USERNAME/RABBITMQ_DEFAULT_USER/' | sed 's/RABBITMQ_PASSWORD/RABBITMQ_DEFAULT_PASS/' > ${NOMAD_ALLOC_DIR}/doppler.env"
      }
      env {
        DOPPLER_TOKEN = var.doppler_token
      }
    }

    task "rabbitmq" {
      driver = "docker"

      config { // TODO: Specify a hostname and storage to avoid information loss on reboot. 
        auth_soft_fail = true
        image          = "rabbitmq:3.12-management"
        ports          = ["amqp"]
      }

      template {
        source      = "${NOMAD_ALLOC_DIR}/doppler.env"
        destination = "${NOMAD_SECRETS_DIR}/doppler.env"
        env         = true
      }

      resources {
        cpu    = 500  # MHz
        memory = 1024 # MB
      }
    }
  }
  
  group "index-builder" {
    meta {
      reeval = uuidv4()
    }
    count = var.replicas

    network {
      mode = "bridge"
      port "grpc" {
        to = 5004
      }
    }

    // Longer than default deadlines due to large images.
    update {
      max_parallel      = 2
      min_healthy_time  = "60s"
      healthy_deadline  = "15m"
      progress_deadline = "20m"
      auto_revert       = true
    }

    service {
      name = "index-builder"
      port = "grpc"

      // TODO: Implement health checks once gRPC health check protocol is implemented in application code.

      connect {
        sidecar_service {
          proxy {
            local_service_port = 5004
            upstreams {
              destination_name = "rabbitmq"
              local_bind_port  = 5672
            }
          }
        }
      }
    }

    task "doppler" {
      driver = "docker"
      lifecycle {
        hook    = "prestart"
        sidecar = false
      }
      config {
        image          = "dopplerhq/cli:3"
        auth_soft_fail = true
        entrypoint     = ["/bin/sh", "-c"]
        command        = "doppler --config-dir /secrets/doppler secrets download --no-file --format env | grep -e ATTACHMENT_STATUS_EXCHANGE -e CONV_INDICES_BUCKET_NAME -e NEW_ATTACHMENT_QUEUE -e RABBITMQ_USERNAME -e RABBITMQ_PASSWORD -e CLOUD_STORAGE_CREDENTIALS -e INDEX_DELETION_QUEUE -e GCS_INDEX_BUILDER_BUCKET -e OPENAI_KEY -e CORPUS_FILE_BUCKET -e MERGED_INDICES_BUCKET_NAME -e CORPUS_INDICES_BUCKET > ${NOMAD_ALLOC_DIR}/doppler.env"
      }
      env {
        DOPPLER_TOKEN = var.doppler_token
      }
    }

    task "index-builder" {
      driver = "docker"

      config {
        image              = var.index_builder_image
        force_pull         = true
        auth_soft_fail     = true
        ports              = ["grpc"]
        image_pull_timeout = "15m"
      }

      template {
        source      = "${NOMAD_ALLOC_DIR}/doppler.env"
        destination = "${NOMAD_SECRETS_DIR}/doppler.env"
        env         = true
      }

      resources {
        cpu    = 10000 # MHz
        memory = 8192 # MB
      }

      env {
        RABBITMQHOST = "127.0.0.1"
      }
    }
  }
}