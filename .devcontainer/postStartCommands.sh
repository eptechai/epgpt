#/bin/bash
# Start inner docker containers
docker compose -f /workspace/.devcontainer/inner-docker-compose.yaml up --detach 
## Start Nomad
service nomad start
## Start Consul
service consul start
## Add credentials for GCR
docker-credential-gcr configure-docker --registries=us-docker.pkg.dev

echo "See README.md" for manual setup steps.